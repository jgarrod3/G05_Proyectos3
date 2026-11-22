#!/usr/bin/env python3
# Gazebo (mundo F1L3) + Nav2 + RViz con el mapa del laboratorio.
# Argumento demo:=<guiada|predefinida|autonoma> (por defecto guiada):
#   guiada     -> PBI 3.2: solo Gazebo + Nav2 + RViz, goals desde RViz
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

os.environ.setdefault('TURTLEBOT3_MODEL', 'waffle_pi')

PKG = 'g05_prii3_nav_turtlebot'
DEMOS = {'predefinida': 'predefined_navigation', 'autonoma': 'autonomous_navigation'}


def demo_node(demo, value, executable):
    return Node(
        package=PKG, executable=executable, output='screen',
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(PythonExpression(["'", demo, "' == '", value, "'"])))


def generate_launch_description():
    pkg = get_package_share_directory(PKG)
    demo = LaunchConfiguration('demo')
    tb3_nav = get_package_share_directory('turtlebot3_navigation2')

    return LaunchDescription([
        DeclareLaunchArgument(
            'demo', default_value='guiada',
            choices=['guiada', 'predefinida', 'autonoma'],
            description='guiada (PBI 3.2), predefinida (PBI 3.3) o autonoma (PBI 3.4)'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg, 'launch', 'f1l3_world.launch.py'))),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(tb3_nav, 'launch', 'navigation2.launch.py')),
            launch_arguments={
                'map': os.path.join(pkg, 'maps', 'f1l3.yaml'),
                'use_sim_time': 'true',
                # Explícito: gzserver.launch.py declara params_file='' y lo pisaría
                'params_file': os.path.join(
                    tb3_nav, 'param', 'humble',
                    os.environ['TURTLEBOT3_MODEL'] + '.yaml'),
            }.items()),
    ] + [demo_node(demo, v, exe) for v, exe in DEMOS.items()])
