from setuptools import setup
import os
from glob import glob

package_name = 'eurobot_gazebo'


def tree(src, dst_root):
    """Return data_files entries that install a directory tree recursively."""
    entries = []
    for root, _, files in os.walk(src):
        if files:
            entries.append((os.path.join(dst_root, root),
                            [os.path.join(root, f) for f in files]))
    return entries


setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ] + tree('worlds', os.path.join('share', package_name)),
    install_requires=['setuptools'],
    zip_safe=True,
    description='Custom Eurobot world for Gazebo simulation with TurtleBot3',
    license='Apache License 2.0',    
)
