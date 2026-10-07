import os
import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
from gazebo_msgs.srv import SpawnEntity, DeleteEntity


class SpawnCubo(Node):

    def __init__(self):
        super().__init__('spawn_cubo')

        self.cliente_spawm = self.create_client(
            SpawnEntity,
            '/spawn_entity'
        )
        self.cliente_borrado = self.create_client(
            DeleteEntity,
            '/delete_entity'
        )

        while not self.cliente_spawm.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                'Esperando al servicio /spawn_entity...'
            )

        while not self.cliente_borrado.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                'Esperando al servicio /delete_entity...'
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
                    'Cubo creado; se eliminará en 5 segundos'
                )

                self.timer_borrado = self.create_timer(
                    15.0,
                    self.borrar_cubo
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

    def borrar_cubo(self):
        self.timer_borrado.cancel()

        peticion_borrado = DeleteEntity.Request()
        peticion_borrado.name = 'cubo'

        self.futuro_borrado = self.cliente_borrado.call_async(
            peticion_borrado
        )

        self.futuro_borrado.add_done_callback(
            self.callback_cubo_borrado
        )

    def callback_cubo_borrado(self, futuro):
        try:
            respuesta = futuro.result()

            if respuesta.success:
                self.get_logger().info(
                    'Cubo eliminado correctamente'
                )
            else:
                self.get_logger().error(
                    f'No se pudo eliminar el cubo: '
                    f'{respuesta.status_message}'
                )

        except Exception as error:
            self.get_logger().error(
                f'Error al eliminar el cubo: {error}'
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