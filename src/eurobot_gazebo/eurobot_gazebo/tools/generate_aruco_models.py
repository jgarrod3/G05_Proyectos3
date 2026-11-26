#!/usr/bin/env python3
"""Genera modelos de Gazebo con marcadores ArUco (textura + material + modelo).

Cada modelo aruco_<ID> es una placa de 12,5 x 12,5 cm con el marcador, igual que
worlds/models/aruco_3. Se usan como textura del ArUco que lleva el robot
(turtlebot3_waffle_aruco) y también se pueden colocar sueltos en el mundo.

Diccionario DICT_4X4_100: contiene los mismos marcadores que DICT_4X4_50 (IDs 0-49,
los del tablero) y además los IDs 50-99.

Uso:
    python3 tools/generate_aruco_models.py              # IDs 51 a 59
    python3 tools/generate_aruco_models.py 60 61 62     # IDs concretos
"""
import os
import sys

import cv2

DICTIONARY = cv2.aruco.DICT_4X4_100
TEXTURE_PX = 600          # resolución de la textura (6 bits x 100 px)
SIZE = 0.125              # lado del marcador (m)

MODEL_SDF = """<?xml version='1.0'?>
<sdf version='1.6'>
  <model name='aruco_{id}'>
    <static>false</static>
    <link name='aruco_link'>
      <collision name='collision'>
        <geometry>
          <box>
            <size>{size} {size} 0.001</size>
          </box>
        </geometry>
      </collision>
      <visual name='aruco_visual'>
        <geometry>
          <box>
            <size>{size} {size} 0.001</size>
          </box>
        </geometry>
        <material>
          <script>
            <uri>model://aruco_{id}/materials/scripts/</uri>
            <uri>model://aruco_{id}/materials/textures/</uri>
            <name>aruco_{id}/aruco_{id}_material</name>
          </script>
        </material>
      </visual>
      <inertial>
        <mass>0.01</mass>
        <inertia>
          <ixx>0.00001</ixx>
          <iyy>0.00001</iyy>
          <izz>0.00001</izz>
        </inertia>
      </inertial>
      <pose>0 0 0 0 0 1.5708</pose>
    </link>
  </model>
</sdf>
"""

MODEL_CONFIG = """<?xml version='1.0'?>
<model>
  <name>aruco_{id}</name>
  <version>1.0</version>
  <sdf version='1.6'>model.sdf</sdf>
  <description>ArUco {id} (DICT_4X4_100), {size_cm} cm. Generado por tools/generate_aruco_models.py</description>
</model>
"""

MATERIAL = """material aruco_{id}/aruco_{id}_material
{{
  technique
  {{
    pass
    {{
      texture_unit
      {{
        texture aruco_{id}.png
      }}
    }}
  }}
}}
"""


def draw_marker(dictionary, marker_id, px):
    if hasattr(cv2.aruco, 'generateImageMarker'):     # OpenCV >= 4.7
        return cv2.aruco.generateImageMarker(dictionary, marker_id, px)
    return cv2.aruco.drawMarker(dictionary, marker_id, px)


def main():
    ids = [int(a) for a in sys.argv[1:]] or list(range(51, 60))
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'worlds', 'models')
    dictionary = cv2.aruco.getPredefinedDictionary(DICTIONARY)

    for marker_id in ids:
        root = os.path.join(models_dir, f'aruco_{marker_id}')
        os.makedirs(os.path.join(root, 'materials', 'scripts'), exist_ok=True)
        os.makedirs(os.path.join(root, 'materials', 'textures'), exist_ok=True)
        fmt = {'id': marker_id, 'size': SIZE, 'size_cm': SIZE * 100}
        cv2.imwrite(os.path.join(root, 'materials', 'textures', f'aruco_{marker_id}.png'),
                    draw_marker(dictionary, marker_id, TEXTURE_PX))
        with open(os.path.join(root, 'materials', 'scripts', f'aruco_{marker_id}.material'), 'w') as f:
            f.write(MATERIAL.format(**fmt))
        with open(os.path.join(root, 'model.sdf'), 'w') as f:
            f.write(MODEL_SDF.format(**fmt))
        with open(os.path.join(root, 'model.config'), 'w') as f:
            f.write(MODEL_CONFIG.format(**fmt))
        print(os.path.normpath(root))


if __name__ == '__main__':
    main()
