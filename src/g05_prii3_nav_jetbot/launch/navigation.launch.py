#!/usr/bin/env python3
# JetBot real: driver (jetbot_pro_ros2) + Nav2 con el mapa F1L3 + RViz.
# Argumento demo:=<guiada|predefinida|autonoma> (por defecto guiada):
#   guiada     -> PBI 3.2: solo Nav2 + RViz, goals desde RViz
#   predefinida-> PBI 3.3: además lanza el nodo predefined_navigation
#   autonoma   -> PBI 3.4: además lanza el nodo autonomous_navigation
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node

PKG = 'g05_prii3_nav_jetbot'
DEMOS = {'predefinida': 'predefined_navigation', 'autonoma': 'autonomous_navigation'}


def generate_launch_description():
    pkg = get_package_share_directory(PKG)
    nav2 = get_package_share_directory('nav2_bringup')

    use_driver = LaunchConfiguration('use_driver')
    use_rviz = LaunchConfiguration('use_rviz')
    map_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    demo = LaunchConfiguration('demo')
    image_topic = LaunchConfiguration('image_topic')

    ld = LaunchDescription([
        # use_driver:=false para lanzar solo Nav2 desde el PC (driver ya corriendo en el JetBot)
        DeclareLaunchArgument('use_driver', default_value='true'),
        DeclareLaunchArgument('use_rviz', default_value='true'),
        DeclareLaunchArgument(
            'demo', default_value='guiada',
            choices=['guiada', 'predefinida', 'autonoma'],
            description='guiada (PBI 3.2), predefinida (PBI 3.3) o autonoma (PBI 3.4)'),
        DeclareLaunchArgument('image_topic', default_value='/image_raw',
                              description='Topic de la cámara para leer el ArUco'),
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

    # Nodo de la demo elegida (BasicNavigator ya espera a que Nav2 esté activo)
    for value, executable in DEMOS.items():
        ld.add_action(Node(
            package=PKG, executable=executable, output='screen',
            parameters=[{'image_topic': image_topic}] if value == 'autonoma' else [],
            condition=IfCondition(PythonExpression(["'", demo, "' == '", value, "'"]))))

    # El driver solo existe en el JetBot: se incluye si está instalado y use_driver:=true
    try:
        jetbot = get_package_share_directory('jetbot_pro_ros2')
        ld.add_action(IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(jetbot, 'launch', 'jetbot.py')),
            condition=IfCondition(use_driver)))
    except Exception:
        print(f'[{PKG}] jetbot_pro_ros2 no encontrado: se lanza solo Nav2')

    return ld
