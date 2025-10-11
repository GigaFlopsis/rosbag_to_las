"""
Setup script for rosbag_to_las converter
Автоматическое определение платформы и установка зависимостей
"""
from setuptools import setup, find_packages
import sys
import platform

# Определяем платформу
is_macos = platform.system() == 'Darwin'
is_linux = platform.system() == 'Linux'

# Базовые зависимости (работают везде)
base_requirements = [
    'numpy>=1.19.0',
    'scipy>=1.5.0',
    'scikit-learn>=0.24.0',
    'matplotlib>=3.3.0',
    'laspy>=2.0.0',
    'lazrs>=0.4.0',
]

# Платформо-специфичные зависимости
platform_requirements = []

if is_macos:
    # На macOS используем rospypi
    print("🍎 Detected macOS: installing ROS dependencies via rospypi...")
    platform_requirements = [
        'rospy>=1.15.0',
        'rosbag>=1.15.0',
        'sensor-msgs>=1.13.0',
        'geometry-msgs>=1.13.0',
        'nav-msgs>=1.13.0',
    ]
elif is_linux:
    # На Linux предполагаем системный ROS
    print("🐧 Detected Linux: assuming system ROS installation")
    print("⚠️  Make sure ROS Noetic is installed:")
    print("    sudo apt install ros-noetic-desktop-full")
    print("    source /opt/ros/noetic/setup.bash")
else:
    print(f"⚠️  Platform {platform.system()} not explicitly supported")
    print("    Attempting to install ROS via rospypi...")
    platform_requirements = [
        'rospy>=1.15.0',
        'rosbag>=1.15.0',
        'sensor-msgs>=1.13.0',
        'geometry-msgs>=1.13.0',
        'nav-msgs>=1.13.0',
    ]

# Объединяем зависимости
all_requirements = base_requirements + platform_requirements

setup(
    name='rosbag_to_las',
    version='2.0.0',
    description='ROS Bag to LAS/LAZ converter with SLAM optimization',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/eddie3ruff/bag2laz',
    py_modules=['bag2las', 'bag2las_transform'],
    install_requires=all_requirements,
    dependency_links=[
        'https://rospypi.github.io/simple/',
    ] if is_macos else [],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    entry_points={
        'console_scripts': [
            'bag2las=bag2las:main',
            'bag2las-transform=bag2las_transform:main',
        ],
    },
)
