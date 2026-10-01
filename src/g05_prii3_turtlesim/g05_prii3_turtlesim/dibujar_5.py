import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool, Empty
from std_srvs.srv import Empty as EmptySrv
import math

class Dibujar5Node(Node):
    def __init__(self):
        super().__init__('dibujar_5_node')
        
        # Publicador de velocidad
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        
        # Cliente para resetear el simulador turtlesim por defecto
        self.reset_client = self.create_client(EmptySrv, '/reset')
        
        # Servicios propios requeridos en el PBI 1.3
        self.pause_srv = self.create_service(SetBool, 'pause_resume_drawing', self.pause_callback)
        self.reset_srv = self.create_service(Empty, 'reset_drawing', self.reset_callback)
        
        # Temporizador a 10 Hz (0.1 segundos)
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        # Variables de control
        self.is_paused = False
        self.state = 0
        self.start_time = self.get_clock().now()

    def pause_callback(self, request, response):
        self.is_paused = request.data
        estado_str = "Pausado" if self.is_paused else "Reanudado"
        self.get_logger().info(f'Dibujo {estado_str}')
        response.success = True
        response.message = f'Estado cambiado a: {estado_str}'
        return response

    def reset_callback(self, request, response):
        self.get_logger().info('Reiniciando el dibujo...')
        self.is_paused = False
        self.state = 0
        
        # Llamar al servicio nativo de turtlesim para limpiar la pantalla y centrar la tortuga
        if self.reset_client.wait_for_service(timeout_sec=1.0):
            req = EmptySrv.Request()
            self.reset_client.call_async(req)
            
        self.start_time = self.get_clock().now()
        return response

    def timer_callback(self):
        if self.is_paused:
            # Si está pausado, enviamos velocidad 0 para detener a la tortuga
            msg = Twist()
            self.publisher_.publish(msg)
            # Actualizamos el start_time para no perder la noción del tiempo de la fase actual
            self.start_time = self.get_clock().now() - rclpy.time.Duration(seconds=self.current_duration)
            return

        msg = Twist()
        now = self.get_clock().now()
        self.current_duration = (now - self.start_time).nanoseconds / 1e9

        # Máquina de estados para dibujar el número 5
        # La tortuga empieza mirando hacia la derecha.
        
        if self.state == 0:
            # Girar 180 grados para empezar trazando la línea superior hacia la izquierda
            msg.angular.z = math.pi
            if self.current_duration > 1.0:
                self.change_state(1)
                
        elif self.state == 1:
            # Trazar línea superior
            msg.linear.x = 2.0
            if self.current_duration > 1.0:
                self.change_state(2)
                
        elif self.state == 2:
            # Girar 90 grados a la izquierda (para mirar hacia abajo)
            msg.angular.z = math.pi / 2
            if self.current_duration > 1.0:
                self.change_state(3)
                
        elif self.state == 3:
            # Trazar línea vertical corta
            msg.linear.x = 1.5
            if self.current_duration > 1.0:
                self.change_state(4)
                
        elif self.state == 4:
            # Girar 90 grados a la izquierda (para mirar hacia la derecha)
            msg.angular.z = math.pi / 2
            if self.current_duration > 1.0:
                self.change_state(5)
                
        elif self.state == 5:
            # Trazar la "barriga" del 5 (semicírculo hacia abajo y a la izquierda)
            # Combinamos avance con giro negativo (hacia la derecha desde la perspectiva de la tortuga)
            msg.linear.x = 2.0
            msg.angular.z = -math.pi / 1.5
            if self.current_duration > 2.0:
                self.change_state(6)
                
        elif self.state == 6:
            # Dibujo terminado, nos quedamos quietos
            msg.linear.x = 0.0
            msg.angular.z = 0.0

        self.publisher_.publish(msg)

    def change_state(self, new_state):
        self.state = new_state
        self.start_time = self.get_clock().now()

def main(args=None):
    rclpy.init(args=args)
    node = Dibujar5Node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()