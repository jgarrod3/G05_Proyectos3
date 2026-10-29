from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'g05_prii3_move_jetbot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='juan',
    maintainer_email='jgarrod3@upv.edu.es',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'draw_number = g05_prii3_move_jetbot.draw_number:main',
            'collision_avoidance = g05_prii3_move_jetbot.collision_avoidance:main',
            'obstacle_avoidance_avoidance = g05_prii3_move_jetbot.obstacle_avoidance:main'
        ],
    },
)
