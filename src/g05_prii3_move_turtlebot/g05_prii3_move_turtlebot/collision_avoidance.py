import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class CollisionAvoidance(Node):
    def __init__(self):
        super().__init__('collision_avoidance')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.callback_lidar,
            10
        )

        self.distancia_segura = 0.30

    def callback_lidar(self, msg):
        limite_angular = math.radians(30)

        distancias_validas = [
            distancia
            for i, distancia in enumerate(msg.ranges)
            if -limite_angular <= msg.angle_min + i * msg.angle_increment <= limite_angular
            and math.isfinite(distancia)
            and msg.range_min <= distancia <= msg.range_max
        ]
        min_distancia = min(distancias_validas, default=float('inf'))
        if min_distancia < self.distancia_segura:
            movimiento = Twist()
            movimiento.linear.x = 0.0
            movimiento.angular.z = 0.0
            self.publisher.publish(movimiento)

def main(args=None):
    rclpy.init(args=args)

    nodo = CollisionAvoidance()

    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()