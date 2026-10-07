import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class ObstacleAvoidance(Node):

    def __init__(self):
        super().__init__('obstacle_avoidance')

        self.orden_dibujo = Twist()
        self.esquivando = False

        self.publisher_cmd_vel = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.subscription_dibujo = self.create_subscription(
            Twist,
            '/cmd_vel_dibujo',
            self.callback_dibujo,
            10
        )

        self.subscription_lidar = self.create_subscription(
            LaserScan,
            '/scan',
            self.callback_lidar,
            10
        )

        self.get_logger().info('Nodo obstacle_avoidance iniciado.')

    def callback_dibujo(self, msg):
        self.orden_dibujo = msg

        if not self.esquivando:
            self.publisher_cmd_vel.publish(self.orden_dibujo)

    def callback_lidar(self, msg):
        frente = self.minimo_en_sector(msg, -0.35, 0.35)

        if frente < 0.5:
            self.esquivando = True

            orden_segura = Twist()
            orden_segura.linear.x = 0.0
            orden_segura.angular.z = 0.8

            self.publisher_cmd_vel.publish(orden_segura)

            self.get_logger().info(
                f'OBSTACULO: frente={frente:.2f}. Girando a la izquierda.'
            )

        else:
            if self.esquivando:
                self.get_logger().info('Camino libre. Retomando el dibujo.')

            self.esquivando = False
            self.publisher_cmd_vel.publish(self.orden_dibujo)

    def minimo_en_sector(self, scan, angulo_inicio, angulo_fin):
        distancias_validas = []

        for i, distancia in enumerate(scan.ranges):
            angulo = scan.angle_min + i * scan.angle_increment

            if angulo_inicio <= angulo <= angulo_fin:
                if (
                    not math.isinf(distancia)
                    and not math.isnan(distancia)
                    and scan.range_min <= distancia <= scan.range_max
                ):
                    distancias_validas.append(distancia)

        if not distancias_validas:
            return float('inf')

        return min(distancias_validas)


def main(args=None):
    rclpy.init(args=args)

    nodo = ObstacleAvoidance()

    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()