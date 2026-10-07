import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_srvs.srv import SetBool

class CollisionAvoidance(Node):
    def __init__(self):
        super().__init__('collision_avoidance')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.callback_lidar,
            10
        )

        self.cliente_pausa = self.create_client(
            SetBool,
            'pause_resume_drawing'
        )
        while not self.cliente_pausa.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                'Esperando al servicio pause_resume_drawing...'
    )
        
        self.obstaculo_detectado = False
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
            if not self.obstaculo_detectado:
                request = SetBool.Request()
                request.data = True
                self.cliente_pausa.call_async(request)
                self.obstaculo_detectado = True

        else:
            if self.obstaculo_detectado:
                request = SetBool.Request()
                request.data = False
                self.cliente_pausa.call_async(request)
                self.obstaculo_detectado = False

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