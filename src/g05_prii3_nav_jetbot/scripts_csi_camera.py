#!/usr/bin/env python3
# Publica la cámara CSI de la Jetson en /image_raw.
# Uso: python3 scripts_csi_camera.py [sensor_id]   (por defecto 1 = conector CAM1)
import sys

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


def gst_pipeline(sensor_id, w=640, h=480, fps=15):
    return (f'nvarguscamerasrc sensor-id={sensor_id} ! '
            f'video/x-raw(memory:NVMM),width={w},height={h},framerate={fps}/1 ! '
            'nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! '
            'video/x-raw,format=BGR ! appsink drop=1 max-buffers=1')


class CsiCamera(Node):
    def __init__(self, sensor_id):
        super().__init__('csi_camera')
        self.cap = cv2.VideoCapture(gst_pipeline(sensor_id), cv2.CAP_GSTREAMER)
        if not self.cap.isOpened():
            raise RuntimeError(f'No se pudo abrir la cámara sensor-id={sensor_id}')
        self.pub = self.create_publisher(Image, '/image_raw', 10)
        self.bridge = CvBridge()
        self.create_timer(1.0 / 15, self.tick)
        self.get_logger().info(f'Publicando cámara sensor-id={sensor_id} en /image_raw')

    def tick(self):
        ok, frame = self.cap.read()
        if not ok:
            self.get_logger().warn('Frame no leído', throttle_duration_sec=2.0)
            return
        msg = self.bridge.cv2_to_imgmsg(frame, 'bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera_link'
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = CsiCamera(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
    try:
        rclpy.spin(node)
    finally:
        node.cap.release()


if __name__ == '__main__':
    main()
