import os
import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
from gazebo_msgs.srv import SpawnEntity


class SpawnCubo(Node):

    def __init__(self):
        super().__init__('spawn_cubo')

        self.cliente_spawm = self.create_client(
            SpawnEntity,
            '/spawn_entity'
        )

        while not self.cliente_spawm.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                'Esperando al servicio /spawn_entity...'
            )


        ruta_paquete = get_package_share_directory(
            'g05_prii3_move_turtlebot'
        )

        ruta_sdf = os.path.join(
            ruta_paquete,
            'models',
            'cubo.sdf'
        )

        with open(ruta_sdf, 'r') as archivo:
            contenido_sdf = archivo.read()

        request = SpawnEntity.Request()
        request.name = 'cubo'
        request.xml = contenido_sdf
        request.robot_namespace = ''
        request.initial_pose.position.x = 0.5
        request.initial_pose.position.y = 0.5
        request.initial_pose.position.z = 0.0
        request.reference_frame = 'world'

        self.futuro = self.cliente_spawm.call_async(request)
        self.futuro.add_done_callback(self.callback_cubo_creado)

    def callback_cubo_creado(self, futuro):
        try:
            respuesta = futuro.result()

            if respuesta.success:
                self.get_logger().info(
                    'Cubo creado'
                )
            else:
                self.get_logger().error(
                    f'No se pudo crear el cubo: '
                    f'{respuesta.status_message}'
                )

        except Exception as error:
            self.get_logger().error(
                f'Error al crear el cubo: {error}'
            )


def main(args=None):
    rclpy.init(args=args)

    nodo = SpawnCubo()

    try:
        rclpy.spin(nodo)
    except KeyboardInterrupt:
        pass
    finally:
        nodo.destroy_node()
        rclpy.shutdown()




if __name__ == '__main__':
    main()