import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import Empty, SetBool

class DrawNumber(Node):

    def __init__(self):
        super().__init__("draw_number")

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.publicar_movimiento)

        #Resetea la posición del robot al arrancar
        self.client_reset = self.create_client(Empty, '/reset_world')
        #while not self.client_reset.wait_for_service(timeout_sec=1.0):
         #   self.get_logger().info('Esperando servicio /reset_world...')
        #self.client_reset.call_async(Empty.Request())

        self.iteracion = 0

        #Servicio de pausa
        self.pausado = False
        self.servicio_pausa = self.create_service(
            SetBool, 'pause_resume_drawing', self.callback_pausa)

        #Servicio de Reinicio
        self.servicio_reinicio = self.create_service(
            Empty, 'reset_drawing', self.callback_reinicio)

    def publicar_movimiento(self):
        if self.pausado:
            mensaje = Twist()
            self.publisher.publish(mensaje)
            return
        mensaje = Twist()

        if self.iteracion < 50:
            mensaje.linear.x = 0.10
            mensaje.angular.z = 0.0
        elif self.iteracion < 80:
            mensaje.linear.x = 0.0
            mensaje.angular.z = 0.531
        elif self.iteracion < 130:
            mensaje.linear.x = 0.10
            mensaje.angular.z = 0.0
        elif self.iteracion < 160:
            mensaje.linear.x = 0.0
            mensaje.angular.z = 0.531
        elif self.iteracion < 210:
            mensaje.linear.x = 0.10
            mensaje.angular.z = 0.0
        elif self.iteracion < 240:
            mensaje.linear.x = 0.0
            mensaje.angular.z = -0.531
        elif self.iteracion < 290:
            mensaje.linear.x = 0.10
            mensaje.angular.z = 0.0
        elif self.iteracion < 320:
            mensaje.linear.x = 0.0
            mensaje.angular.z = -0.531
        elif self.iteracion < 370:
            mensaje.linear.x = 0.10
            mensaje.angular.z = 0.0 
        else:
            mensaje.linear.x = 0.0
            mensaje.angular.z = 0.0

        self.publisher.publish(mensaje)
        self.iteracion += 1


    def callback_pausa(self, request, response):
        self.pausado = request.data
        response.success = True

        if self.pausado:
            response.message = 'Dibujo pausado'
            self.get_logger().info('Dibujo pausado')
        else:
            response.message = 'Dibujo reanudado'
            self.get_logger().info('Dibujo reanudado')
        return response

    def callback_reinicio(self, request, response):
        self.pausado = False
        self.iteracion = 0
        self.client_reset.call_async(Empty.Request())
        self.get_logger().info('Dibujo reiniciado')
        return response
    
def main(args=None):
    rclpy.init(args=args)
    nodo = DrawNumber()
    rclpy.spin(nodo)
    nodo.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()