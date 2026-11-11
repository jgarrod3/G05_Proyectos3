#!/usr/bin/env python3
"""
PBI 3.1 - Deteccion de ArUcos del tablero Eurobot 2027 con camara cenital (USB).
Publica en un topic (std_msgs/String, formato JSON) el id y las coordenadas
de todos los ArUcos detectados en cada frame. Si no se detecta ninguno,
publica "[]", asi en el echo se ve como desaparecen.
"""
import json
import os

import cv2
import numpy as np
import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from std_msgs.msg import String


def load_calibration(path):
    """Lee K y D de un yaml de calibracion (formato ROS o formato OpenCV)."""
    with open(path) as f:
        first = f.readline()
    if first.startswith('%YAML'):  # formato cv2.FileStorage
        fs = cv2.FileStorage(path, cv2.FILE_STORAGE_READ)
        K = fs.getNode('camera_matrix').mat()
        D = fs.getNode('distortion_coefficients').mat()
        fs.release()
    else:  # formato ROS (camera_calibration)
        with open(path) as f:
            data = yaml.safe_load(f)
        K = np.array(data['camera_matrix']['data'], dtype=np.float64).reshape(3, 3)
        D = np.array(data['distortion_coefficients']['data'], dtype=np.float64)
    return K, D


def default_calib_path():
    """Busca config/camera_calibration.yaml (o .yml) dentro del paquete instalado."""
    config = os.path.join(get_package_share_directory('g05_prii3_vision'), 'config')
    for name in ('camera_calibration.yaml', 'camera_calibration.yml'):
        path = os.path.join(config, name)
        if os.path.exists(path):
            return path
    return os.path.join(config, 'camera_calibration.yaml')


class ArucoCenital(Node):
    def __init__(self):
        super().__init__('aruco_cenital')

        # Parametros (se pueden cambiar con --ros-args -p nombre:=valor)
        self.declare_parameter('camera_index', 4)      # /dev/video4 = WEB CAM (USB)
        self.declare_parameter('width', 1280)          # 16:9 -> mas campo de vision
        self.declare_parameter('height', 720)
        self.declare_parameter('use_calibration', False)
        self.declare_parameter('fps', 15.0)
        self.declare_parameter('alpha', 1.0)           # 0 = recorta, 1 = imagen completa
        self.declare_parameter('show_image', True)
        self.declare_parameter('topic', '/g05/arucos')
        self.declare_parameter('calib_file', '')       # vacio = config/ del paquete

        cam = self.get_parameter('camera_index').value
        fps = float(self.get_parameter('fps').value)
        self.alpha = float(self.get_parameter('alpha').value)
        self.show = bool(self.get_parameter('show_image').value)
        topic = self.get_parameter('topic').value

        # Calibracion de la camara
        self.K, self.D = None, None
        if self.get_parameter('use_calibration').value:
            calib = self.get_parameter('calib_file').value or default_calib_path()
            try:
                self.K, self.D = load_calibration(calib)
                self.get_logger().info(f'Calibracion cargada: {calib}')
            except Exception as e:
                self.get_logger().warn(f'Sin calibracion ({e}), imagen sin corregir')
        else:
            self.get_logger().info('Calibracion desactivada, imagen en bruto')
        self.maps = None  # mapas de undistort, se calculan con el primer frame

        # Camara USB
        self.cap = cv2.VideoCapture(cam, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            self.get_logger().error(f'No se pudo abrir la camara {cam}')
            raise SystemExit(1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.get_parameter('width').value)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.get_parameter('height').value)

        # Diccionario Eurobot 2027
        dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)

        # Compatibilidad OpenCV < 4.7 y >= 4.7
        if hasattr(cv2.aruco, 'ArucoDetector'):
            detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
            self.detect = detector.detectMarkers
        else:
            params = cv2.aruco.DetectorParameters_create()
            self.detect = lambda img: cv2.aruco.detectMarkers(img, dictionary, parameters=params)

        self.pub = self.create_publisher(String, topic, 10)
        self.timer = self.create_timer(1.0 / fps, self.loop)
        self.get_logger().info(f'Publicando ArUcos en {topic}')

    def undistort(self, frame):
        if self.K is None:
            return frame
        if self.maps is None:
            h, w = frame.shape[:2]
            newK, _ = cv2.getOptimalNewCameraMatrix(self.K, self.D, (w, h), self.alpha, (w, h))
            self.maps = cv2.initUndistortRectifyMap(
                self.K, self.D, None, newK, (w, h), cv2.CV_16SC2)
            self.get_logger().info(f'Undistort preparado ({w}x{h}, alpha={self.alpha})')
        return cv2.remap(frame, self.maps[0], self.maps[1], cv2.INTER_LINEAR)

    def loop(self):
        ok, frame = self.cap.read()
        if not ok:
            self.get_logger().warn('Frame no leido', throttle_duration_sec=2.0)
            return

        frame = self.undistort(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.detect(gray)

        markers = []
        if ids is not None:
            for c, i in zip(corners, ids.flatten()):
                cx, cy = c.reshape(4, 2).mean(axis=0)
                markers.append({'id': int(i), 'x': round(float(cx), 1), 'y': round(float(cy), 1)})
            if self.show:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        markers.sort(key=lambda m: m['id'])
        msg = String()
        msg.data = json.dumps(markers)
        self.pub.publish(msg)

        if self.show:
            cv2.imshow('aruco_cenital', frame)
            cv2.waitKey(1)

    def destroy_node(self):
        self.cap.release()
        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ArucoCenital()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()