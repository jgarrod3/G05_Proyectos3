# PBI 4.2 - Navegación guiada por odometría en el tablero Eurobot.
# Desde el centro, lleva el robot uno detrás de otro a los cuatro ArUco del tablero y lo
# devuelve al centro. Cada objetivo se envía a la acción /navigate_to_pose
# (nav2_msgs/action/NavigateToPose) en el frame 'map' y se espera su resultado antes de
# mandar el siguiente. Sirve igual en simulación y en el JetBot real (mismas coordenadas).
#
# No se usa BasicNavigator: su waitUntilNav2Active() espera a AMCL y aquí no hay AMCL.
import math
import time

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node

# Coordenadas del reglamento Eurobot (frame 'map'): tablero de 0-3 x 0-2 m.
CENTER = (1.5, 1.0)
ARUCOS = {  # id: (x, y)
    22: (0.6, 0.6),
    20: (0.6, 1.4),
    21: (2.4, 1.4),
    23: (2.4, 0.6),
}
TOUR = [22, 20, 21, 23]  # recorrido en sentido horario visto desde arriba
FINAL_YAW = math.pi      # al volver al centro, misma orientación que al empezar
REJECT_RETRIES = 30      # x 2 s: margen para que Nav2 (y Gazebo) terminen de arrancar

STATUS_NAMES = {
    GoalStatus.STATUS_SUCCEEDED: 'SUCCEEDED',
    GoalStatus.STATUS_ABORTED: 'ABORTED',
    GoalStatus.STATUS_CANCELED: 'CANCELED',
}


def heading(a, b):
    """Orientación (rad) para ir del punto a al punto b."""
    return math.atan2(b[1] - a[1], b[0] - a[0])


def build_goals():
    """Lista de (nombre, x, y, yaw). Cada ArUco se alcanza mirando hacia el siguiente tramo,
    así el robot no tiene que girar al llegar y otra vez al salir."""
    points = [('ArUco %d' % i, ARUCOS[i]) for i in TOUR] + [('centro', CENTER)]
    goals = []
    for k, (name, p) in enumerate(points):
        yaw = heading(p, points[k + 1][1]) if k + 1 < len(points) else FINAL_YAW
        goals.append((name, p[0], p[1], yaw))
    return goals


class ArucoTour(Node):

    def __init__(self):
        super().__init__('aruco_tour')
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def make_pose(self, x, y, yaw):
        p = PoseStamped()
        p.header.frame_id = 'map'
        p.header.stamp = self.get_clock().now().to_msg()
        p.pose.position.x = float(x)
        p.pose.position.y = float(y)
        p.pose.orientation.z = math.sin(yaw / 2.0)
        p.pose.orientation.w = math.cos(yaw / 2.0)
        return p

    def feedback_cb(self, msg):
        self.get_logger().info(
            f'  distancia restante: {msg.feedback.distance_remaining:.2f} m',
            throttle_duration_sec=2.0)

    def go_to(self, name, x, y, yaw):
        """Envía un objetivo y bloquea hasta su resultado. Devuelve True si se alcanza."""
        self.get_logger().info(
            f'-> {name}: ({x:.2f}, {y:.2f}, yaw {math.degrees(yaw):.0f} grados)')
        # El servidor de la acción existe antes de que Nav2 termine de activarse y hasta
        # entonces rechaza los objetivos: se reintenta durante un rato.
        for attempt in range(REJECT_RETRIES):
            goal = NavigateToPose.Goal()
            goal.pose = self.make_pose(x, y, yaw)
            send_future = self.client.send_goal_async(goal, feedback_callback=self.feedback_cb)
            rclpy.spin_until_future_complete(self, send_future)
            handle = send_future.result()
            if handle is not None and handle.accepted:
                break
            self.get_logger().warn(f'  objetivo rechazado (¿Nav2 activándose?), reintento '
                                   f'{attempt + 1}/{REJECT_RETRIES}')
            time.sleep(2.0)
        else:
            self.get_logger().error(f'{name}: FALLADO (objetivo rechazado por Nav2)')
            return False

        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        status = result_future.result().status
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info(f'{name}: ALCANZADO')
            return True
        self.get_logger().error(
            f'{name}: FALLADO ({STATUS_NAMES.get(status, "status=%d" % status)})')
        return False

    def run(self):
        self.get_logger().info('Esperando al servidor de acción /navigate_to_pose...')
        while not self.client.wait_for_server(timeout_sec=2.0):
            if not rclpy.ok():
                return
            self.get_logger().info('  ...Nav2 aún no está listo')

        results = [(g[0], self.go_to(*g)) for g in build_goals()]

        self.get_logger().info('===== Resumen =====')
        for name, ok in results:
            self.get_logger().info(f'  {name:9s}: {"ALCANZADO" if ok else "FALLADO"}')
        n_ok = sum(ok for _, ok in results)
        self.get_logger().info(f'{n_ok}/{len(results)} objetivos alcanzados')


def main(args=None):
    rclpy.init(args=args)
    node = ArucoTour()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
