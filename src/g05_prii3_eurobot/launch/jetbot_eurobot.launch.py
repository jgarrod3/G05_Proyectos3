"""PBI 4.2 con el JetBot real: driver + mapa del tablero + Nav2 (sin AMCL) + RViz + recorrido.

    ros2 launch g05_prii3_eurobot jetbot_eurobot.launch.py
    ros2 launch g05_prii3_eurobot jetbot_eurobot.launch.py use_driver:=false  # driver aparte
    ros2 launch g05_prii3_eurobot jetbot_eurobot.launch.py tour:=false        # solo Nav2

Localización solo por odometría: el lidar pasa por encima de la valla, así que no hay AMCL.
La odometría del JetBot empieza en (0, 0, 0) donde arranca el driver, por eso se publica una
TF fija map -> odom con la pose en la que se coloca el robot sobre el tablero (argumentos
x, y, yaw; por defecto el centro mirando hacia x = 0, igual que en la simulación).
Colocar el robot ANTES de arrancar el driver (o reiniciar el driver tras colocarlo).
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

PKG = 'g05_prii3_eurobot'


def generate_launch_description():
    pkg = get_package_share_directory(PKG)
    eurobot = get_package_share_directory('eurobot_gazebo')
    nav2 = get_package_share_directory('nav2_bringup')
    params = {'use_sim_time': False}

    ld = LaunchDescription([
        DeclareLaunchArgument('use_driver', default_value='true',
                              description='Lanzar el driver jetbot_pro_ros2 (si está instalado)'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('tour', default_value='true',
                              description='Lanzar el nodo aruco_tour'),
        DeclareLaunchArgument('x', default_value='1.5', description='x inicial del robot (m)'),
        DeclareLaunchArgument('y', default_value='1.0', description='y inicial del robot (m)'),
        DeclareLaunchArgument('yaw', default_value='3.14159',
                              description='Orientación inicial del robot (rad)'),
        DeclareLaunchArgument('map', default_value=os.path.join(eurobot, 'maps', 'eurobot.yaml'),
                              description='Mapa del tablero'),
        DeclareLaunchArgument('params_file',
                              default_value=os.path.join(pkg, 'config', 'nav2_params_jetbot.yaml'),
                              description='Parámetros de Nav2 para el JetBot'),

        # Mapa del tablero (/map)
        Node(package='nav2_map_server', executable='map_server', name='map_server',
             output='screen',
             parameters=[{'yaml_filename': LaunchConfiguration('map'), **params}]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager',
             name='lifecycle_manager_map', output='screen',
             parameters=[{**params, 'autostart': True, 'node_names': ['map_server']}]),

        # map -> odom fija = pose inicial del robot en el tablero (en vez de AMCL)
        Node(package='tf2_ros', executable='static_transform_publisher',
             name='map_to_odom', output='screen',
             arguments=['--x', LaunchConfiguration('x'), '--y', LaunchConfiguration('y'),
                        '--yaw', LaunchConfiguration('yaw'),
                        '--frame-id', 'map', '--child-frame-id', 'odom']),

        # Servidores de Nav2 (planner, controller, behaviors, bt_navigator, ...), sin AMCL
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav2, 'launch', 'navigation_launch.py')),
            launch_arguments={'use_sim_time': 'false',
                              'params_file': LaunchConfiguration('params_file'),
                              'autostart': 'true'}.items()),

        Node(package='rviz2', executable='rviz2', name='rviz2', output='screen',
             arguments=['-d', os.path.join(nav2, 'rviz', 'nav2_default_view.rviz')],
             condition=IfCondition(LaunchConfiguration('rviz'))),

        Node(package=PKG, executable='aruco_tour', output='screen', parameters=[params],
             condition=IfCondition(LaunchConfiguration('tour'))),
    ])

    # El driver solo existe en el JetBot: se incluye si está instalado y use_driver:=true
    try:
        jetbot = get_package_share_directory('jetbot_pro_ros2')
        ld.add_action(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(jetbot, 'launch', 'jetbot.py')),
            condition=IfCondition(LaunchConfiguration('use_driver'))))
    except Exception:
        print(f'[{PKG}] jetbot_pro_ros2 no encontrado: se lanza sin driver')

    return ld
