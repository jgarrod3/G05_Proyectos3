#!/usr/bin/env python3
# PBI 3.2: Gazebo (mundo F1L3) + Nav2 + RViz con el mapa del laboratorio.
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

os.environ.setdefault('TURTLEBOT3_MODEL', 'waffle_pi')


def generate_launch_description():
    pkg = get_package_share_directory('g05_prii_nav_turtlebot')
    tb3_nav = get_package_share_directory('turtlebot3_navigation2')

    return LaunchDescription([
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
    ])
