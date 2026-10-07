from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='g05_prii3_move_turtlebot',
            executable='spawn_cubo',
            name='spawn_cubo',
            output='screen'
        ),
        Node(
            package='g05_prii3_move_turtlebot',
            executable='draw_number',
            name='draw_number',
            output='screen'
        ),

        Node(
            package='g05_prii3_move_turtlebot',
            executable='collision_avoidance',
            name='collision_avoidance',
            output='screen'
        ),
    ])