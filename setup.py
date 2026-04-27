from setuptools import setup, find_packages

package_name = 'ibn_attitude'

setup(
    name=package_name,
    version='0.0.0',

    packages=find_packages(include=['ibn_attitude', 'ibn_attitude.*']),

    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch',
            ['src/ibn_attitude/launch/pixhawk_bridge.launch.py']),
    ],
    
    install_requires=['setuptools'],
    zip_safe=True,

    maintainer='you',
    maintainer_email='you@todo.todo',
    description='IBN attitude system',
    license='TODO',

    entry_points={
        'console_scripts': [
            'pixhawk_telemetry = ibn_attitude.nodes.pixhawk_telemetry:main',
            'gps_injection = ibn_attitude.nodes.gps_injection:main',
        ],
    },
)