from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Nodo 1: El simulador de turtlesim
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='simulador_tortuga'
        ),
        # Nodo 2: Script para dibujar el 5
        Node(
            package='g05_prii3_turtlesim',
            executable='dibujar_5',
            name='dibujar_5_node'
        )
    ])