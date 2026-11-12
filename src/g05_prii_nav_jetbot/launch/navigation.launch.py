#!/usr/bin/env python3
# JetBot real: driver (jetbot_pro_ros2) + Nav2 con el mapa F1L3 + RViz.
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('g05_prii_nav_jetbot')
    nav2 = get_package_share_directory('nav2_bringup')

    use_driver = LaunchConfiguration('use_driver')
    use_rviz = LaunchConfiguration('use_rviz')
    map_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')

    ld = LaunchDescription([
        # use_driver:=false para lanzar solo Nav2 desde el PC (driver ya corriendo en el JetBot)
        DeclareLaunchArgument('use_driver', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument('map', default_value=os.path.join(pkg, 'maps', 'f1l3.yaml')),
        DeclareLaunchArgument('params_file',
                              default_value=os.path.join(pkg, 'config', 'nav2_params.yaml')),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2, 'launch', 'bringup_launch.py')),
            launch_arguments={
                'map': map_file,
                'use_sim_time': 'false',
                'params_file': params_file,
                'autostart': 'true',
            }.items()),

        Node(
            package='rviz2', executable='rviz2', name='rviz2', output='screen',
            arguments=['-d', os.path.join(nav2, 'rviz', 'nav2_default_view.rviz')],
            condition=IfCondition(use_rviz)),
    ])

    # El driver solo existe en el JetBot: se incluye si está instalado y use_driver:=true
    try:
        jetbot = get_package_share_directory('jetbot_pro_ros2')
        ld.add_action(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(jetbot, 'launch', 'jetbot.py')),
            condition=IfCondition(use_driver)))
    except Exception:
        print('[g05_prii_nav_jetbot] jetbot_pro_ros2 no encontrado: se lanza solo Nav2')

    return ld
