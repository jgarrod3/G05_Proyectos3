"""PBI 4.2 en simulación: mundo Eurobot + Nav2 (sin AMCL) + RViz + recorrido por los ArUco.

    ros2 launch g05_prii3_eurobot sim_eurobot.launch.py
    ros2 launch g05_prii3_eurobot sim_eurobot.launch.py world:=false   # mundo ya abierto
    ros2 launch g05_prii3_eurobot sim_eurobot.launch.py tour:=false    # solo Nav2 + RViz

El robot aparece en el centro del tablero (1.5, 1.0) mirando a x = 0. La TF map -> odom es
fija (identidad): la odometría de Gazebo da la pose en el frame del mundo = 'map'.
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
    eurobot_share = get_package_share_directory('eurobot_gazebo')
    eurobot = os.path.join(eurobot_share, 'launch')

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='true',
                              description='Lanzar Gazebo con el mundo Eurobot'),
        DeclareLaunchArgument('tour', default_value='true',
                              description='Lanzar el nodo aruco_tour'),
        DeclareLaunchArgument('rviz', default_value='true'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(eurobot, 'eurobot_world.launch.py')),
            condition=IfCondition(LaunchConfiguration('world'))),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(eurobot, 'navigation.launch.py')),
            # map y params_file explícitos: gzserver.launch.py declara 'params_file' vacío
            # y, al compartir launch, se colaría en Nav2
            launch_arguments={
                'use_sim_time': 'true',
                'rviz': LaunchConfiguration('rviz'),
                'map': os.path.join(eurobot_share, 'maps', 'eurobot.yaml'),
                'params_file': os.path.join(eurobot_share, 'config', 'nav2_params.yaml'),
            }.items()),

        # El nodo espera solo a que /navigate_to_pose esté disponible
        Node(package='g05_prii3_eurobot', executable='aruco_tour', output='screen',
             parameters=[{'use_sim_time': True}],
             condition=IfCondition(LaunchConfiguration('tour'))),
    ])
