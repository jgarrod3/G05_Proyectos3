"""Nav2 en el tablero Eurobot: mapa + navegación + RViz (sin AMCL).

Lanzar con el mundo abierto (eurobot_world.launch.py):

    ros2 launch eurobot_gazebo navigation.launch.py
    ros2 launch eurobot_gazebo navigation.launch.py rviz:=false

Después se envían objetivos a la acción /navigate_to_pose (nav2_msgs/action/NavigateToPose),
con "Nav2 Goal" en RViz o desde un nodo, en el frame 'map' = coordenadas del reglamento
Eurobot (tablero de 0-3 x 0-2 m). No hace falta fijar la pose inicial.

Por qué no turtlebot3_navigation2: su configuración localiza con AMCL y el lidar, pero el
haz del lidar (~13 cm) pasa por encima de la valla (7 cm). Sin nada que ver, AMCL se pierde
en pocos movimientos. Aquí la TF map -> odom es fija (identidad): en Gazebo la odometría da
la pose en el frame del mundo, que coincide con 'map'. En un robot real la odometría deriva
y haría falta un localizador (p. ej., con la cámara cenital) que publique map -> odom.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('eurobot_gazebo')
    nav2_bringup = get_package_share_directory('nav2_bringup')
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('map', default_value=os.path.join(pkg, 'maps', 'eurobot.yaml'),
                              description='Mapa del tablero'),
        DeclareLaunchArgument('params_file',
                              default_value=os.path.join(pkg, 'config', 'nav2_params.yaml'),
                              description='Parámetros de Nav2'),
        DeclareLaunchArgument('localization', default_value='true',
                              description='Publicar map->odom fija. Ponlo a false si otro '
                                          'nodo publica map->odom'),
        DeclareLaunchArgument('rviz', default_value='true'),

        # Mapa del tablero (/map)
        Node(
            package='nav2_map_server', executable='map_server', name='map_server',
            output='screen',
            parameters=[{'yaml_filename': LaunchConfiguration('map'),
                         'use_sim_time': use_sim_time}],
        ),
        Node(
            package='nav2_lifecycle_manager', executable='lifecycle_manager',
            name='lifecycle_manager_map', output='screen',
            parameters=[{'use_sim_time': use_sim_time, 'autostart': True,
                         'node_names': ['map_server']}],
        ),

        # map -> odom fija (en vez de AMCL)
        Node(
            package='tf2_ros', executable='static_transform_publisher',
            name='map_to_odom', output='screen',
            arguments=['--frame-id', 'map', '--child-frame-id', 'odom'],
            parameters=[{'use_sim_time': use_sim_time}],
            condition=IfCondition(LaunchConfiguration('localization')),
        ),

        # Servidores de Nav2 (planner, controller, behaviors, bt_navigator, velocity_smoother...)
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_bringup, 'launch', 'navigation_launch.py')),
            launch_arguments={
                'use_sim_time': use_sim_time,
                'params_file': LaunchConfiguration('params_file'),
                'autostart': 'true',
            }.items(),
        ),

        Node(
            package='rviz2', executable='rviz2', name='rviz2', output='screen',
            arguments=['-d', os.path.join(nav2_bringup, 'rviz', 'nav2_default_view.rviz')],
            parameters=[{'use_sim_time': use_sim_time}],
            condition=IfCondition(LaunchConfiguration('rviz')),
        ),
    ])
