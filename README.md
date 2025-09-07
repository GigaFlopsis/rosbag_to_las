# bag2laz

## Overview
`bag2laz` is a versatile Python utility designed to convert various point cloud data formats into LAS or LAZ files. It supports multiple input formats including ROSbag, CSV, PCAP, and XYZ, making LiDAR data more accessible and viewable across different platforms using standard point cloud processing tools like CloudCompare.

## Features
- **Multiple Input Formats:** Converts ROSbag (`sensor_msgs/PointCloud2`), CSV, PCAP, and XYZ files into LAS or LAZ files.
- **Cross-Platform Compatibility:** Enables the use of converted files on different operating systems, with appropriate point cloud visualization tools.
- **Support for ROS Noetic:** ROSbag conversions are specifically supported under ROS Noetic on Ubuntu 20.04.

## Prerequisites
- **Python Packages:** The script requires `laspy` and `numpy`. These can be installed via pip:
  ```shell
  pip install laspy numpy
  ```
  Additional requirements for ROSbag conversions:
  - **ROS Noetic:** Ensure that ROS Noetic is installed and properly set up on your Ubuntu 20.04 system.
  - **rosbag:** Typically installed with ROS Noetic.

## Installation
Clone the repository to your local machine using:
```shell
git clone https://github.com/eddie3ruff/bag2laz.git
```

## Usage
To use `bag2laz`, simply edit the `/path/to/bags/` and `/path/to/converted_bags/` in the script. You can choose LAZ or LAS depending on the file extension setting.

### Example
Once the paths are set, you would run the following in a terminal window:

```shell
python3 bag2laz.py
```

## Output
The script will process each `.bag` file in the specified directory, converting it to a `.laz` file saved in the specified output directory. The conversion status and any errors will be displayed in the terminal.

## Contributing
Contributions to `bag2laz` are welcome! Please feel free to fork the repository, make your changes, and submit a pull request.

## License
[MIT](https://opensource.org/licenses/MIT)



## macos install

```shell
pip install --extra-index-url https://rospypi.github.io/simple/ rospy rosbag geometry_msgs sensor_msgs
```

# Установите один из LAZ бэкендов
pip install lazrs
# или
pip install laszip
