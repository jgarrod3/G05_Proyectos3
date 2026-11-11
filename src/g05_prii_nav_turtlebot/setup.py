from glob import glob
import os
from setuptools import setup

package_name = 'g05_prii_nav_turtlebot'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ] + [
        (os.path.join('share', package_name, os.path.dirname(f)), [f])
        for f in glob('models/**/*.*', recursive=True)
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    description='Custom F1L3 world for Gazebo simulation with TurtleBot3',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'predefined_navigation = g05_prii_nav_turtlebot.predefined_navigation:main',
            'autonomous_navigation = g05_prii_nav_turtlebot.autonomous_navigation:main',
        ],
    },
)
