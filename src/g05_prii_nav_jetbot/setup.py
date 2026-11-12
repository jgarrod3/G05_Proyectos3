from glob import glob
import os
from setuptools import setup

package_name = 'g05_prii_nav_jetbot'

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
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='juan',
    maintainer_email='jgarrod3@upv.edu.es',
    description='Navegación Nav2 del JetBot real en el laboratorio F1L3',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'predefined_navigation = g05_prii_nav_jetbot.predefined_navigation:main',
            'autonomous_navigation = g05_prii_nav_jetbot.autonomous_navigation:main',
        ],
    },
)
