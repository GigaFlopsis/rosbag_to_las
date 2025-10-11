# ROS Bag to LAS Converter with SLAM Integration

## Overview
Advanced Python utility for converting ROS bag files containing PointCloud2 data into LAS/LAZ format with integrated SLAM (Simultaneous Localization and Mapping) optimization. The tool supports multiple transformation modes and provides high-quality point cloud maps with automatic trajectory correction and loop closure detection.

## ✨ New Features (SLAM Integration)
- **🤖 SLAM Optimization**: Pose graph optimization with loop closure detection
- **🔄 Trajectory Correction**: Automatic drift correction and trajectory smoothing  
- **📊 Visualization**: Comprehensive trajectory comparison plots
- **🎯 Multiple Modes**: Transform modes from sensor coordinates to globally optimized maps
- **📈 Quality Metrics**: Detailed analysis of trajectory improvements

## Core Features
- **Multiple Input Formats:** ROSbag (`sensor_msgs/PointCloud2`), CSV, PCAP, and XYZ conversion to LAS/LAZ
- **Advanced Transformations:** Sensor coordinates, global odometry, SLAM-optimized global coordinates
- **Cross-Platform Compatibility:** Works across different operating systems with standard point cloud tools
- **ROS Integration:** Full support for ROS Noetic on Ubuntu 20.04 and macOS

## SLAM Capabilities

### Transformation Modes
1. **🚫 No Transformation**: Original sensor coordinates
2. **🌍 Global Coordinates**: Standard odometry-based transformation  
3. **🌍 Global + SLAM**: **Recommended** - SLAM-optimized global coordinates
4. **📍 Local Coordinates**: Relative to first scan position

### SLAM Features
- **Loop Closure Detection**: Automatic detection of revisited locations
- **Pose Graph Optimization**: Mathematical optimization using least squares
- **Drift Correction**: Eliminates accumulated odometry errors
- **Quality Assessment**: Comprehensive metrics for trajectory evaluation

## Prerequisites

### ⚡ Quick Start Options

1. **Docker (Easiest)** - Works on all platforms with zero dependency issues
2. **Auto-installer** - Platform-specific automatic setup (`install.sh` / `install.bat`)
3. **Manual** - Traditional pip install for advanced users

### Core Dependencies
- Python 3.6+
- numpy, scipy, scikit-learn, matplotlib
- laspy (LAS/LAZ file handling)
- lazrs or laszip (LAZ compression)
- ROS packages (rosbag, sensor_msgs) - installed automatically

**📚 See [INSTALL.md](INSTALL.md) for detailed platform-specific instructions**

## Installation
```shell
git clone https://github.com/eddie3ruff/bag2laz.git
cd bag2laz

# Use automatic installer (recommended)
./install.sh  # macOS/Linux
# or install.bat on Windows

# Or install manually
pip install -r requirements.txt  # or requirements-macos.txt / requirements-linux.txt
```

**💡 First time user?** See [INSTALL.md](INSTALL.md) for platform-specific guide

## Usage

### Interactive Mode (Recommended)
```shell
python bag2las_transform.py
```

The script will guide you through:
1. **Input selection**: Choose bag file or directory
2. **Topic selection**: Select PointCloud2 topic from available topics
3. **Transform mode**: Choose transformation mode (select #3 for SLAM)
4. **Processing**: Automatic conversion with real-time progress

### Example SLAM Output
```
🤖 ПРИМЕНЕНИЕ SLAM ОПТИМИЗАЦИИ...
📊 Добавление 1247 поз в граф...
🔍 Поиск замыканий циклов...
   ✅ Найдено потенциальных кандидатов: 23
   🎯 Подтверждено замыканий циклов: 8

📊 РЕЗУЛЬТАТЫ SLAM ОПТИМИЗАЦИИ:
   • Найдено loop closures: 8
   • Исходная длина траектории: 1247.85 м
   • Оптимизированная длина: 1251.23 м  
   • Исходный дрифт: 4.234 м → 0.567 м
   • Среднее изменение позиции: 0.845 м
```

## Output Files

After processing, you'll get:
- **`bagname.laz`**: Main point cloud file (LAS/LAZ format)
- **`bagname.pos`**: Trajectory file in POS format  
- **`bagname_slam_trajectory_comparison.png`**: SLAM visualization plots

## SLAM Documentation

For detailed SLAM information, see:
- **[SLAM_DOCUMENTATION.md](SLAM_DOCUMENTATION.md)**: Complete technical documentation
- **[SLAM_USER_GUIDE.md](SLAM_USER_GUIDE.md)**: User-friendly guide and troubleshooting

## When to Use SLAM

### ✅ Recommended for:
- Long trajectories with loops and returns (>500m)
- Data with noticeable odometry drift
- Indoor/structured environment mapping
- High accuracy requirements

### ❌ Not necessary for:
- Short straight trajectories (<100m)  
- High-precision odometry (RTK GPS)
- Open spaces without revisits
- Quick processing priority

## Contributing
Contributions are welcome! Please fork the repository, make changes, and submit a pull request.

## License
[MIT](https://opensource.org/licenses/MIT)

---

## Installation

### 🚀 Quick Install (Recommended)

#### Automatic Installation:
```bash
# macOS / Linux
chmod +x install.sh
./install.sh

# Windows
install.bat
```

#### Docker (Universal Solution):
```bash
docker build -t rosbag_to_las .
docker run -it -v $(pwd)/data:/data rosbag_to_las
```

### 📋 Manual Installation

#### macOS:
```bash
pip install -r requirements-macos.txt
```

#### Linux:
```bash
# With system ROS (recommended)
sudo apt install ros-noetic-desktop-full
source /opt/ros/noetic/setup.bash
pip install -r requirements-linux.txt

# Without system ROS
pip install -r requirements.txt
```

#### Windows:
```bash
pip install -r requirements.txt
```

**📚 Detailed installation guide:** [INSTALL.md](INSTALL.md)