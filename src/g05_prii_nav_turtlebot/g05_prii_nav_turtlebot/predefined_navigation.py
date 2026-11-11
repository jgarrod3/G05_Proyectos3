# PBI 3.3: del punto inicial del pasillo a un punto fijo dentro del laboratorio.
import rclpy

from g05_prii_nav_turtlebot.nav_utils import go_to, start_navigator

GOAL_POSE = (1.0, 7.5, 1.57)  # dentro del laboratorio (frame map)


def main():
    rclpy.init()
    nav = start_navigator()
    go_to(nav, GOAL_POSE, 'destino predefinido')
    nav.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
