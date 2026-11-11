# PBI 3.4: pasillo -> puerta -> leer ArUco (DICT_4X4_100) -> pose final según el ID.
import time

import cv2
import rclpy
from cv_bridge import CvBridge
from sensor_msgs.msg import Image

from g05_prii_nav_turtlebot.nav_utils import go_to, start_navigator

DOOR_POSE = (3.65, 0.4, 1.57)  # en el pasillo, mirando hacia la puerta del lab

# ID ArUco -> pose final dentro del laboratorio (frame map)
ARUCO_POSES = {
    5: (-2.5, 7.0, 3.14),
    6: (2.5, 8.0, 0.0),
    17: (3.0, 14.0, 1.57),
}

DETECT_TIMEOUT = 20.0  # s


def main():
    rclpy.init()
    nav = start_navigator()

    if not go_to(nav, DOOR_POSE, 'puerta'):
        rclpy.shutdown()
        return

    # --- Detección del ArUco con la cámara del robot ---
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
    detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
    bridge = CvBridge()
    found = []

    def on_image(msg):
        if found:
            return
        gray = bridge.imgmsg_to_cv2(msg, 'mono8')
        _, ids, _ = detector.detectMarkers(gray)
        if ids is not None:
            for i in ids.flatten():
                if int(i) in ARUCO_POSES:
                    found.append(int(i))
                    return
            nav.get_logger().warn(f'ArUco desconocido: {ids.flatten().tolist()}',
                                  throttle_duration_sec=2.0)

    sub = nav.create_subscription(Image, '/camera/image_raw', on_image, 10)
    nav.get_logger().info('Buscando ArUco en la puerta...')
    t0 = time.time()
    while not found and time.time() - t0 < DETECT_TIMEOUT:
        rclpy.spin_once(nav, timeout_sec=0.1)
    nav.destroy_subscription(sub)

    if not found:
        nav.get_logger().error('No se ha detectado ningún ArUco válido')
    else:
        aruco_id = found[0]
        nav.get_logger().info(f'ArUco {aruco_id} detectado')
        go_to(nav, ARUCO_POSES[aruco_id], f'destino ArUco {aruco_id}')

    nav.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
