import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'g05_prii3_move_turtlebot'

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
        (os.path.join('share', package_name, 'models'),
            glob('models/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='juan',
    maintainer_email='jgarrod3@upv.edu.es',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'draw_number = g05_prii3_move_turtlebot.draw_number:main',
            'collision_avoidance = g05_prii3_move_turtlebot.collision_avoidance:main',
            'spawn_cubo = g05_prii3_move_turtlebot.spawn_cubo:main',
        ],
    },
)
