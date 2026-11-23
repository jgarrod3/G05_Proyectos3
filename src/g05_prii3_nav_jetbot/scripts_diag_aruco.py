#!/usr/bin/env python3
# Diagnóstico ArUco: python3 scripts_diag_aruco.py [topic]   (por defecto /image_raw)
# Muestra frames recibidos, encoding/resolución y prueba varios diccionarios.
import sys

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image

DICTS = {n: getattr(cv2.aruco, n) for n in [
    'DICT_4X4_50', 'DICT_5X5_100', 'DICT_6X6_250', 'DICT_7X7_250', 'DICT_ARUCO_ORIGINAL']}


class Diag(Node):
    def __init__(self, topic):
        super().__init__('aruco_diag')
        self.bridge = CvBridge()
        self.n = 0
        self.detectors = {}
        for name, d in DICTS.items():
            dic = cv2.aruco.getPredefinedDictionary(d)
            if hasattr(cv2.aruco, 'ArucoDetector'):
                self.detectors[name] = cv2.aruco.ArucoDetector(
                    dic, cv2.aruco.DetectorParameters()).detectMarkers
            else:
                p = cv2.aruco.DetectorParameters_create()
                self.detectors[name] = (
                    lambda img, dic=dic, p=p: cv2.aruco.detectMarkers(img, dic, parameters=p))
        # QoS best-effort: compatible con publicadores reliable y best-effort
        self.create_subscription(Image, topic, self.cb, qos_profile_sensor_data)
        self.get_logger().info(f'Escuchando {topic} ...')

    def cb(self, msg):
        self.n += 1
        if self.n == 1:
            self.get_logger().info(f'Primer frame: {msg.width}x{msg.height} encoding={msg.encoding}')
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hits = []
        for name, det in self.detectors.items():
            corners, ids, rejected = det(gray)
            if ids is not None:
                hits.append(f'{name}: {ids.flatten().tolist()}')
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        if hits:
            self.get_logger().info(' | '.join(hits), throttle_duration_sec=1.0)
        else:
            self.get_logger().info(f'frame {self.n}: nada (candidatos rechazados: {len(rejected)})',
                                   throttle_duration_sec=2.0)
        if self.n % 30 == 1:  # guarda un frame de vez en cuando para revisarlo
            cv2.imwrite('/home/juan/aruco_frame.png', frame)
        cv2.imshow('aruco_diag', frame)
        cv2.waitKey(1)


def main():
    rclpy.init()
    rclpy.spin(Diag(sys.argv[1] if len(sys.argv) > 1 else '/image_raw'))


if __name__ == '__main__':
    main()
