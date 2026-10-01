# PRII3 - Sprint 1: Robots Inteligentes (Grupo 5)

Este repositorio contiene el workspace de ROS2 para el Sprint 1, cumpliendo con la implementación de un nodo autónomo para `turtlesim`.

## 1. Despliegue y Ejecución (PBI 1.1 - 1.4)
**Requisitos:** Ubuntu 22.04 y ROS2 Humble.

**Instalación y Compilación:**
1. Clonar el repositorio: `git clone <https://github.com/jgarrod3/G05_Proyectos3.git> ~/g05_prii3_ws`
2. Compilar: `cd ~/g05_prii3_ws && colcon build`
3. Cargar entorno: `source /opt/ros/humble/setup.bash && source install/setup.bash`

**Ejecución Principal:**
Para lanzar el simulador y el nodo de control simultáneamente desde un único archivo, ejecutar:
`ros2 launch g05_prii3_turtlesim turtlesim_group5.launch.py`

**Control por Servicios:**
En una nueva terminal (`source ~/g05_prii3_ws/install/setup.bash`), utilizar:
* **Pausar:** `ros2 service call /pause_resume_drawing std_srvs/srv/SetBool "{data: true}"`
* **Reanudar:** `ros2 service call /pause_resume_drawing std_srvs/srv/SetBool "{data: false}"`
* **Reiniciar (limpiar pantalla):** `ros2 service call /reset_drawing std_srvs/srv/Empty`

## 2. Arquitectura del Software (PBI 1.3)
El sistema se compone de un entorno ROS2 interactuando mediante tópicos y servicios:
* **El Nodo (Cerebro):** Desarrollado en Python, calcula la trayectoria para dibujar el número 5 utilizando una máquina de estados controlada por un temporizador (Timer) a 10 Hz. 
* **Tópicos y Mensajes:** El nodo publica mensajes de tipo `Twist` (velocidad lineal y angular) en el tópico de movimiento, al cual el simulador está suscrito.
* **Servicios ROS:** Se han implementado servidores que modifican las variables internas del nodo para pausar, reanudar y reiniciar el comportamiento en tiempo real sin interrumpir el proceso principal.

