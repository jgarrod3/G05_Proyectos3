# JetBot real: pasillo -> puerta -> leer ArUco (DICT_5X5_100) -> pose final según el ID.
import math
import time

import cv2
import rclpy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

# Poses en el frame "map" (x, y, yaw). El origen del mapa es donde arranca el robot.
INITIAL_POSE = (0.0, 0.0, 0.0)  # pasillo (spawn del robot)

DOOR_POSE = (3.65, 0.4, 1.57)  # en el pasillo, mirando hacia la puerta del lab

# ID ArUco -> pose final dentro del laboratorio (frame map)
ARUCO_POSES = {
    5: (-2.5, 7.0, 3.14),
    6: (-3.1, 14.5, 3.14),  # esquina izquierda del fondo del laboratorio
    17: (3.0, 14.0, 1.57),
}

DETECT_TIMEOUT = 20.0  # s


def make_pose(nav, x, y, yaw):
    p = PoseStamped()
    p.header.frame_id = 'map'
    p.header.stamp = nav.get_clock().now().to_msg()
    p.pose.position.x = float(x)
    p.pose.position.y = float(y)
    p.pose.orientation.z = math.sin(yaw / 2.0)
    p.pose.orientation.w = math.cos(yaw / 2.0)
    return p


def start_navigator():
    nav = BasicNavigator()
    nav.setInitialPose(make_pose(nav, *INITIAL_POSE))
    nav.waitUntilNav2Active()
    return nav


def go_to(nav, pose, name=''):
    nav.get_logger().info(f'Navegando a {name} {pose}')
    nav.goToPose(make_pose(nav, *pose))
    while not nav.isTaskComplete():
        fb = nav.getFeedback()
        if fb:
            nav.get_logger().info(
                f'Distancia restante: {fb.distance_remaining:.2f} m',
                throttle_duration_sec=2.0)
    ok = nav.getResult() == TaskResult.SUCCEEDED
    nav.get_logger().info(f'{name}: {"alcanzado" if ok else "FALLO"}')
    return ok


def main():
    rclpy.init()
    nav = start_navigator()

    if not go_to(nav, DOOR_POSE, 'puerta'):
        rclpy.shutdown()
        return

    # --- Detección del ArUco con la cámara del robot ---
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
    detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
    bridge = CvBridge()
    found = []

    def on_image(msg):
        if found:
            return
        gray = bridge.imgmsg_to_cv2(msg, 'mono8')
        _, ids, _ = detector.detectMarkers(gray)
        if ids is not None:
            for i in ids.flatten():
                if int(i) in ARUCO_POSES:
                    found.append(int(i))
                    return
            nav.get_logger().warn(f'ArUco desconocido: {ids.flatten().tolist()}',
                                  throttle_duration_sec=2.0)

    # Tópico de la cámara del JetBot (cambiar con: --ros-args -p image_topic:=...)
    image_topic = nav.declare_parameter('image_topic', '/image_raw').value
    sub = nav.create_subscription(Image, image_topic, on_image, 10)
    nav.get_logger().info('Buscando ArUco en la puerta...')
    t0 = time.time()
    while not found and time.time() - t0 < DETECT_TIMEOUT:
        rclpy.spin_once(nav, timeout_sec=0.1)
    nav.destroy_subscription(sub)

    if not found:
        nav.get_logger().error('No se ha detectado ningún ArUco válido')
    else:
        aruco_id = found[0]
        nav.get_logger().info(f'ArUco {aruco_id} detectado')
        go_to(nav, ARUCO_POSES[aruco_id], f'destino ArUco {aruco_id}')

    nav.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
