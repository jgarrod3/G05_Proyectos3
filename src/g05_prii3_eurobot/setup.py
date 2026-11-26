from glob import glob
import os
from setuptools import setup

package_name = 'g05_prii3_eurobot'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='juan',
    maintainer_email='jgarrod3@upv.edu.es',
    description='Sprint 4: navegación en el tablero Eurobot (simulación y JetBot real)',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'aruco_tour = g05_prii3_eurobot.aruco_tour:main',
        ],
    },
)
