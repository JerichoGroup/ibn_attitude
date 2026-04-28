from setuptools import setup, find_packages

package_name = 'ibn_mavlink'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(include=['ibn_mavlink', 'ibn_mavlink.*']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config',
            ['ibn_mavlink/config/pixhawk_bridge.yaml', 'ibn_mavlink/config/gps_injection.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=False,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='MAVLink bridge for Pixhawk telemetry',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            'gps_injection = ibn_mavlink.gps_injection.node:main',
            'pixhawk_bridge = ibn_mavlink.pixhawk_bridge.node:main',
        ],
    },
)