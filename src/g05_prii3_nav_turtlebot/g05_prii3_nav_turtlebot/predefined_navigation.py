# PBI 3.3: del punto inicial del pasillo a un punto fijo dentro del laboratorio.
import math

import rclpy

from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

# Poses en el frame "map" (x, y, yaw). El origen del mapa es donde arranca el robot.
INITIAL_POSE = (0.0, 0.0, 0.0)  # pasillo (spawn del robot)

GOAL_POSE = (1.0, 7.5, 1.57)  # dentro del laboratorio (frame map)


def make_pose(nav, x, y, yaw):
    p = PoseStamped()
    p.header.frame_id = 'map'
    p.header.stamp = nav.get_clock().now().to_msg()
    p.pose.position.x = float(x)
    p.pose.position.y = float(y)
    p.pose.orientation.z = math.sin(yaw / 2.0)
    p.pose.orientation.w = math.cos(yaw / 2.0)
    return p


def start_navigator():
    nav = BasicNavigator()
    nav.setInitialPose(make_pose(nav, *INITIAL_POSE))
    nav.waitUntilNav2Active()
    return nav


def go_to(nav, pose, name=''):
    nav.get_logger().info(f'Navegando a {name} {pose}')
    nav.goToPose(make_pose(nav, *pose))
    while not nav.isTaskComplete():
        fb = nav.getFeedback()
        if fb:
            nav.get_logger().info(
                f'Distancia restante: {fb.distance_remaining:.2f} m',
                throttle_duration_sec=2.0)
    ok = nav.getResult() == TaskResult.SUCCEEDED
    nav.get_logger().info(f'{name}: {"alcanzado" if ok else "FALLO"}')
    return ok


def main():
    rclpy.init()
    nav = start_navigator()
    go_to(nav, GOAL_POSE, 'destino predefinido')
    nav.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
