/usr/bin/python3 "/Users/devitt/Documents/rosbag_to_las/bag2las copy.py"                                                           
(base) devitt@devitts-MacBook-Pro rosbag_to_las % /usr/bin/python3 "/Users/devitt/Documents/rosbag_to_las/bag2las copy.py"
Failed to load Python extension for LZ4 support. LZ4 compression will not be available.
/Users/devitt/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:34: NotOpenSSLWarning: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(
🚀 КОНВЕРТЕР ROS BAG В LAS
================================================================================
Версия 2.0 - Поддержка выбора файлов и директорий

🎯 ВЫБЕРИТЕ РЕЖИМ РАБОТЫ:
==================================================
1. 📁 Обработать всю директорию (.bag файлы)
2. 📄 Обработать конкретный файл (.bag)
3. ❌ Выход

Введите номер (1-3): 1
📂 Введите путь к директории (или Enter для текущей): 

📁 Директория для сохранения (Enter для '/Users/devitt/Documents/rosbag_to_las'): ^C
👋 Программа прервана пользователем
(base) devitt@devitts-MacBook-Pro rosbag_to_las % /usr/bin/python3 "/Users/devitt/Documents/rosbag_to_las/bag2las copy.py"
Failed to load Python extension for LZ4 support. LZ4 compression will not be available.
/Users/devitt/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:34: NotOpenSSLWarning: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(
🚀 КОНВЕРТЕР ROS BAG В LAS
================================================================================
Версия 2.0 - Поддержка выбора файлов и директорий

🎯 ВЫБЕРИТЕ РЕЖИМ РАБОТЫ:
==================================================
1. 📁 Обработать всю директорию (.bag файлы)
2. 📄 Обработать конкретный файл (.bag)
3. ❌ Выход

Введите номер (1-3): 1
📂 Введите путь к директории (или Enter для текущей): .

📁 Директория для сохранения (Enter для '.'): 
🎯 ОБРАБОТКА ДИРЕКТОРИИ
============================================================
📂 Входная директория: .
📁 Выходная директория: .
🔍 Найдено 1 .bag файл(ов)
    1. 12_2025-09-17-16-31-50.bag (180.4 МБ)
📊 Общий размер: 180.4 МБ

❓ Обработать все 1 файлов? (y/n): y

🔄 [100.0%] Обработка файла 1/1: 12_2025-09-17-16-31-50.bag
============================================================
================================================================================
STARTING CONVERSION: 12_2025-09-17-16-31-50.bag
================================================================================

🔍 ПОЛНЫЙ АНАЛИЗ ТОПИКОВ В BAG ФАЙЛЕ
================================================================================
📂 Файл: 12_2025-09-17-16-31-50.bag
📊 Общая информация:
   • Всего топиков: 19
   • Всего сообщений: 22,436
   • Длительность: 44.05 секунд (0.73 минут)
   • Средняя частота: 509.4 сообщений/сек
   • Время начала: 2025-09-17 16:31:50
   • Время окончания: 2025-09-17 16:32:34

📋 ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ПО ТОПИКАМ:
--------------------------------------------------------------------------------
  № |                  Топик                   |            Тип            |   Сообщ. |  Частота
--------------------------------------------------------------------------------
  1 | /cloud_registered                        | PointCloud2               |      441 |  10.0 Hz
  2 | /diagnostics                             | DiagnosticArray..         |       64 |   2.0 Hz
  3 | /jtop_monitor/cpu/avg                    | Float32                   |       44 |   1.0 Hz
  4 | /jtop_monitor/cpu/full                   | Float32MultiArray..       |       44 |   1.0 Hz
  5 | /jtop_monitor/cpu/max                    | Float32                   |       44 |   1.0 Hz
  6 | /jtop_monitor/cpu/min                    | Float32                   |       44 |   1.0 Hz
  7 | /jtop_monitor/gpu                        | Float32                   |       44 |   1.0 Hz
  8 | /jtop_monitor/ram                        | Float32                   |       44 |   1.0 Hz
  9 | /jtop_monitor/temperatures/cpu           | Float32                   |       44 |   1.0 Hz
 10 | /livox/lidar                             | CustomMsg..               |      441 |  10.0 Hz
 11 | /mavros/altitude                         | Altitude                  |    1,320 |  30.2 Hz
 12 | /mavros/battery                          | BatteryState              |      242 |   5.0 Hz
 13 | /mavros/imu/data                         | Imu                       |    7,547 | 170.3 Hz
 14 | /mavros/local_position/odom              | Odometry                  |    2,633 |  62.0 Hz
 15 | /mavros/state                            | State                     |       45 |   1.0 Hz
 16 | /mavros/statustext/send                  | StatusText                |       13 |   0.2 Hz
 17 | /mavros/vision_pose/pose                 | PoseStamped               |    3,380 | 186.6 Hz
 18 | /tf                                      | TFMessage                 |    6,000 | 213.4 Hz
 19 | /tf_static                               | TFMessage                 |        2 | 1530.8 Hz
--------------------------------------------------------------------------------

🎯 КАТЕГОРИИ ТОПИКОВ:
--------------------------------------------------
📡 PointCloud2 топики (1):
   • /cloud_registered (441 сообщений, 10.0 Hz)

🧭 Odometry топики (1):
   • /mavros/local_position/odom (2,633 сообщений, 62.0 Hz)

🎯 IMU топики (1):
   • /mavros/imu/data (7,547 сообщений, 170.3 Hz)

🔗 Transform топики (2):
   • /tf (6,000 сообщений, 213.4 Hz)
   • /tf_static (2 сообщений, 1530.8 Hz)

📦 Другие топики (14):
   📄 diagnostic_msgs/DiagnosticArray:
      • /diagnostics (64 сообщений, 2.0 Hz)
   📄 geometry_msgs/PoseStamped:
      • /mavros/vision_pose/pose (3,380 сообщений, 186.6 Hz)
   📄 livox_ros_driver2/CustomMsg:
      • /livox/lidar (441 сообщений, 10.0 Hz)
   📄 mavros_msgs/Altitude:
      • /mavros/altitude (1,320 сообщений, 30.2 Hz)
   📄 mavros_msgs/State:
      • /mavros/state (45 сообщений, 1.0 Hz)
   📄 mavros_msgs/StatusText:
      • /mavros/statustext/send (13 сообщений, 0.2 Hz)
   📄 sensor_msgs/BatteryState:
      • /mavros/battery (242 сообщений, 5.0 Hz)
   📄 std_msgs/Float32:
      • /jtop_monitor/cpu/avg (44 сообщений, 1.0 Hz)
      • /jtop_monitor/cpu/max (44 сообщений, 1.0 Hz)
      • /jtop_monitor/cpu/min (44 сообщений, 1.0 Hz)
      • /jtop_monitor/gpu (44 сообщений, 1.0 Hz)
      • /jtop_monitor/ram (44 сообщений, 1.0 Hz)
      • /jtop_monitor/temperatures/cpu (44 сообщений, 1.0 Hz)
   📄 std_msgs/Float32MultiArray:
      • /jtop_monitor/cpu/full (44 сообщений, 1.0 Hz)

✅ АНАЛИЗ ЗАВЕРШЕН:
   • PointCloud2 топиков: 1
   • Odometry топиков: 1
   • Других топиков: 17

📋 Нажмите Enter для продолжения обработки...
🔍 Scanning bag file for PointCloud2 topics...
   📊 Analyzing 22,436 messages...
   📈 Scan progress: 4% (898/22,436)
   📈 Scan progress: 9% (2,020/22,436)
   📈 Scan progress: 14% (3,142/22,436)
   📈 Scan progress: 19% (4,263/22,436)
   📈 Scan progress: 24% (5,385/22,436)
   📈 Scan progress: 29% (6,507/22,436)
   📈 Scan progress: 34% (7,629/22,436)
   📈 Scan progress: 39% (8,751/22,436)
   📈 Scan progress: 44% (9,872/22,436)
   📈 Scan progress: 49% (10,994/22,436)
   📈 Scan progress: 54% (12,116/22,436)
   📈 Scan progress: 59% (13,238/22,436)
   📈 Scan progress: 64% (14,360/22,436)
   📈 Scan progress: 69% (15,481/22,436)
   📈 Scan progress: 74% (16,603/22,436)
   📈 Scan progress: 79% (17,725/22,436)
   📈 Scan progress: 84% (18,847/22,436)
   📈 Scan progress: 89% (19,969/22,436)
   📈 Scan progress: 94% (21,090/22,436)
   📈 Scan progress: 99% (22,212/22,436)
   ✅ Found PointCloud2 topics: {'/cloud_registered': 441}
✅ Only one PointCloud2 topic found: /cloud_registered (441 messages)
   🔄 Using automatically...
✅ Processing topic: /cloud_registered

🧭 ПОИСК ТОПИКОВ ОДОМЕТРИИ...
🔍 Scanning bag file for Odometry topics...
   📊 Analyzing 22,436 messages for odometry...
   📈 Odometry scan progress: 9% (2,020/22,436)
   📈 Odometry scan progress: 19% (4,263/22,436)
   📈 Odometry scan progress: 29% (6,507/22,436)
   📈 Odometry scan progress: 39% (8,751/22,436)
   📈 Odometry scan progress: 49% (10,994/22,436)
   📈 Odometry scan progress: 59% (13,238/22,436)
   📈 Odometry scan progress: 69% (15,481/22,436)
   📈 Odometry scan progress: 79% (17,725/22,436)
   📈 Odometry scan progress: 89% (19,969/22,436)
   📈 Odometry scan progress: 99% (22,212/22,436)
   ✅ Found Odometry topics: {'/mavros/local_position/odom': 2633}
✅ Only one Odometry topic found: /mavros/local_position/odom (2,633 messages)
   🔄 Using automatically for .POS file generation...
📊 Topic details:
   • Messages: 441
   • Frequency: ~10.01 Hz
   • Duration: 44.00 seconds
   • Time range: 1758115910.764 - 1758115954.760
📂 Opening ROS bag file: ./12_2025-09-17-16-31-50.bag
📊 Analyzing bag file structure...
   • Total topics: 19
   • PointCloud2 messages: 441
   • Message type: sensor_msgs/PointCloud2
   • Frequency: ~10.01 Hz
📈 Counting PointCloud2 messages...
   ✅ Total messages to process: 441

🔍 ANALYZING MESSAGE STRUCTURE...
--------------------------------------------------
🔎 Reading first message for field analysis...
   ✅ First message loaded
   ✅ Successfully read 10 sample points
   🔍 First point structure: 8 fields
   🔍 First point values: (0.8853300213813782, -2.2946701049804688, 2.1359291076660156, 0.0, 0.0, 0.0, 71.5, 0.0)
   📊 NaN points in sample: 0/10
📋 Available fields (8): ['x', 'y', 'z', 'intensity', 'normal_x', 'normal_y', 'normal_z', 'curvature']

🖥️  SYSTEM INFO:
   • OS: Darwin 24.6.0
   • Python: 3.9.6
   • sensor_msgs version: unknown
   • numpy version: 1.26.1
   • laspy version: 2.6.1

📊 Detailed field information:
    1. x               | Type: FLOAT32  | Offset:   0 | Count: 1
    2. y               | Type: FLOAT32  | Offset:   4 | Count: 1
    3. z               | Type: FLOAT32  | Offset:   8 | Count: 1
    4. intensity       | Type: FLOAT32  | Offset:  32 | Count: 1
    5. normal_x        | Type: FLOAT32  | Offset:  16 | Count: 1
    6. normal_y        | Type: FLOAT32  | Offset:  20 | Count: 1
    7. normal_z        | Type: FLOAT32  | Offset:  24 | Count: 1
    8. curvature       | Type: FLOAT32  | Offset:  36 | Count: 1

📐 PointCloud2 dimensions:
   • Width: 693
   • Height: 1
   • Points per message: 693
   • Point step: 48 bytes
   • Row step: 33264 bytes
   • Is dense: True
   • Header timestamp: 1758115910.690911 (1758115910.690911)
   • Frame ID: 'map'
✅ Will use ROS header timestamp as GPS time

🎯 FIELD EXTRACTION PLAN:
   • Coordinates (x,y,z): ✅ Always included
   • Intensity: ✅ Found in PointCloud2
   • Time: ✅ From ROS header timestamp

📝 Fields to extract: ['x', 'y', 'z', 'intensity']

🔄 PROCESSING MESSAGES...
--------------------------------------------------
🔄 Reopening bag file for processing...
⏱️  Processing started at 21:19:38

🔍 DEBUG Message 1:
   • Width: 693, Height: 1
   • Point step: 48, Row step: 33264
   • Expected points: 693
   • Data length: 33264 bytes
   • Is dense: True
   • Message timestamp: 1758115910.764340
      Point 1: ['0.885330', '-2.294670', '2.135929', '71.500000']
      Point 2: ['-1.255601', '4.305957', '3.777949', '82.000000']
      Point 3: ['-1.601313', '4.293988', '4.085413', '82.500000']
      Point 4: ['-2.827793', '1.123196', '4.322324', '90.000000']
      Point 5: ['-2.392461', '3.298931', '4.404497', '5.000000']
   • Actually read points: 693
   • Points extraction ratio: 100.0%
   • Point data sample: [(0.8853300213813782, -2.2946701049804688, 2.1359291076660156, 71.5), (-1.255601167678833, 4.305956840515137, 3.777949333190918, 82.0), (-1.6013131141662598, 4.29398775100708, 4.085412502288818, 82.5)]
   📊 [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   0.2% | Msg    1/441 | 693 pts | ETA: --:--
   ⏱️  Using uniform timestamp per message for better visualization
   🔍 Message timestamp: 1758115910.764340
      Point 0: ['0.885330', '-2.294670', '2.135929', '71.500000']
         └─ Intensity at index 3: 71.5
         └─ ROS time: 1758115910.764340 (uniform for message)
      Point 1: ['-1.255601', '4.305957', '3.777949', '82.000000']
         └─ Intensity at index 3: 82.0
         └─ ROS time: 1758115910.764340 (uniform for message)
      Point 2: ['-1.601313', '4.293988', '4.085413', '82.500000']
         └─ Intensity at index 3: 82.5
         └─ ROS time: 1758115910.764340 (uniform for message)

🔍 DEBUG Message 2:
   • Width: 628, Height: 1
   • Point step: 48, Row step: 30144
   • Expected points: 628
   • Data length: 30144 bytes
   • Is dense: True
   • Message timestamp: 1758115910.839917
      Point 1: ['-4.094797', '-0.569883', '4.035061', '73.500000']
      Point 2: ['-4.618882', '-0.953330', '4.578166', '2.000000']
      Point 3: ['-4.656301', '-1.197010', '4.655567', '2.000000']
      Point 4: ['-4.584765', '-1.415076', '4.629510', '2.500000']
      Point 5: ['-4.240401', '-1.529781', '4.339684', '36.000000']
   • Actually read points: 628
   • Points extraction ratio: 100.0%
   • Point data sample: [(-4.094797134399414, -0.5698826313018799, 4.035061359405518, 73.5), (-4.618881702423096, -0.9533304572105408, 4.578166484832764, 2.0), (-4.656301498413086, -1.1970103979110718, 4.655566692352295, 2.0)]
   📊 [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   0.5% | Msg    2/441 | 628 pts | ETA: 00:00
       ⚡ Processing rate: 398,663 points/sec | Elapsed: 00:00

🔍 DEBUG Message 3:
   • Width: 659, Height: 1
   • Point step: 48, Row step: 31632
   • Expected points: 659
   • Data length: 31632 bytes
   • Is dense: True
   • Message timestamp: 1758115910.938889
   • Actually read points: 659
   • Points extraction ratio: 100.0%
   • Point data sample: [(5.381001949310303, -2.61556077003479, 0.2746639549732208, 28.5), (6.1613616943359375, -1.8678923845291138, 0.0032184477895498276, 79.0), (2.593593120574951, -0.521931529045105, -0.008612385019659996, 36.79999923706055)]
   📊 [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   0.7% | Msg    3/441 | 659 pts | ETA: 00:00
       ⚡ Processing rate: 505,352 points/sec | Elapsed: 00:00
   📊 [  0.9%] Processing message    4/441 - 641 points
   📊 [  1.1%] Processing message    5/441 - 653 points
   📊 [  1.4%] Processing message    6/441 - 652 points
   📊 [  1.6%] Processing message    7/441 - 636 points
   📊 [  1.8%] Processing message    8/441 - 647 points
   📊 [  2.0%] Processing message    9/441 - 666 points
   📊 [  2.3%] Processing message   10/441 - 570 points
   📊 [  2.5%] Processing message   11/441 - 688 points
   📊 [  2.7%] Processing message   12/441 - 668 points
   📊 [  2.9%] Processing message   13/441 - 699 points
   📊 [  3.2%] Processing message   14/441 - 687 points
   📊 [  3.4%] Processing message   15/441 - 633 points
   📊 [  3.6%] Processing message   16/441 - 659 points
   📊 [  3.9%] Processing message   17/441 - 668 points
   📊 [  4.1%] Processing message   18/441 - 652 points
   📊 [  4.3%] Processing message   19/441 - 643 points
   📊 [  4.5%] Processing message   20/441 - 549 points
   📊 [  4.8%] Processing message   21/441 - 701 points
   📊 [█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   5.0% | Msg   22/441 | 661 pts | ETA: 00:00
       ⚡ Processing rate: 742,756 points/sec | Elapsed: 00:00
   📊 [  5.2%] Processing message   23/441 - 642 points
   📊 [  5.4%] Processing message   24/441 - 612 points
   📊 [  5.7%] Processing message   25/441 - 672 points
   📊 [  5.9%] Processing message   26/441 - 668 points
   📊 [  6.1%] Processing message   27/441 - 661 points
   📊 [  6.3%] Processing message   28/441 - 670 points
   📊 [  6.6%] Processing message   29/441 - 673 points
   📊 [  6.8%] Processing message   30/441 - 628 points
   📊 [  7.0%] Processing message   31/441 - 703 points
   📊 [  7.3%] Processing message   32/441 - 654 points
   📊 [  7.5%] Processing message   33/441 - 628 points
   📊 [  7.7%] Processing message   34/441 - 640 points
   📊 [  7.9%] Processing message   35/441 - 660 points
   📊 [  8.2%] Processing message   36/441 - 681 points
   📊 [  8.4%] Processing message   37/441 - 651 points
   📊 [  8.6%] Processing message   38/441 - 673 points
   📊 [  8.8%] Processing message   39/441 - 696 points
   📊 [  9.1%] Processing message   40/441 - 636 points
   📊 [  9.3%] Processing message   41/441 - 746 points
   📊 [  9.5%] Processing message   42/441 - 731 points
   📊 [  9.8%] Processing message   43/441 - 687 points
   📊 [██░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  10.0% | Msg   44/441 | 717 pts | ETA: 00:00
       ⚡ Processing rate: 794,690 points/sec | Elapsed: 00:00
   📊 [ 10.2%] Processing message   45/441 - 687 points
   📊 [ 10.4%] Processing message   46/441 - 708 points
   📊 [ 10.7%] Processing message   47/441 - 666 points
   📊 [ 10.9%] Processing message   48/441 - 666 points
   📊 [ 11.1%] Processing message   49/441 - 674 points
   📊 [ 11.3%] Processing message   50/441 - 659 points
   📊 [ 11.6%] Processing message   51/441 - 677 points
   📊 [ 11.8%] Processing message   52/441 - 665 points
   📊 [ 12.0%] Processing message   53/441 - 709 points
   📊 [ 12.2%] Processing message   54/441 - 692 points
   📊 [ 12.5%] Processing message   55/441 - 684 points
   📊 [ 12.7%] Processing message   56/441 - 691 points
   📊 [ 12.9%] Processing message   57/441 - 705 points
   📊 [ 13.2%] Processing message   58/441 - 707 points
   📊 [ 13.4%] Processing message   59/441 - 739 points
   📊 [ 13.6%] Processing message   60/441 - 613 points
   📊 [ 13.8%] Processing message   61/441 - 756 points
   📊 [ 14.1%] Processing message   62/441 - 719 points
   📊 [ 14.3%] Processing message   63/441 - 716 points
   📊 [ 14.5%] Processing message   64/441 - 730 points
   📊 [ 14.7%] Processing message   65/441 - 724 points
   📊 [████░░░░░░░░░░░░░░░░░░░░░░░░░░]  15.0% | Msg   66/441 | 731 pts | ETA: 00:00
       ⚡ Processing rate: 812,489 points/sec | Elapsed: 00:00
   📊 [ 15.2%] Processing message   67/441 - 710 points
   📊 [ 15.4%] Processing message   68/441 - 726 points
   📊 [ 15.6%] Processing message   69/441 - 731 points
   📊 [ 15.9%] Processing message   70/441 - 638 points
   📊 [ 16.1%] Processing message   71/441 - 707 points
   📊 [ 16.3%] Processing message   72/441 - 712 points
   📊 [ 16.6%] Processing message   73/441 - 687 points
   📊 [ 16.8%] Processing message   74/441 - 658 points
   📊 [ 17.0%] Processing message   75/441 - 649 points
   📊 [ 17.2%] Processing message   76/441 - 738 points
   📊 [ 17.5%] Processing message   77/441 - 704 points
   📊 [ 17.7%] Processing message   78/441 - 678 points
   📊 [ 17.9%] Processing message   79/441 - 703 points
   📊 [ 18.1%] Processing message   80/441 - 697 points
   📊 [ 18.4%] Processing message   81/441 - 722 points
   📊 [ 18.6%] Processing message   82/441 - 692 points
   📊 [ 18.8%] Processing message   83/441 - 671 points
   📊 [ 19.0%] Processing message   84/441 - 677 points
   📊 [ 19.3%] Processing message   85/441 - 680 points
   📊 [ 19.5%] Processing message   86/441 - 684 points
   📊 [ 19.7%] Processing message   87/441 - 710 points
   📊 [█████░░░░░░░░░░░░░░░░░░░░░░░░░]  20.0% | Msg   88/441 | 688 pts | ETA: 00:00
       ⚡ Processing rate: 823,405 points/sec | Elapsed: 00:00
   📊 [ 20.2%] Processing message   89/441 - 733 points
   📊 [ 20.4%] Processing message   90/441 - 664 points
   📊 [ 20.6%] Processing message   91/441 - 739 points
   📊 [ 20.9%] Processing message   92/441 - 728 points
   📊 [ 21.1%] Processing message   93/441 - 709 points
   📊 [ 21.3%] Processing message   94/441 - 721 points
   📊 [ 21.5%] Processing message   95/441 - 717 points
   📊 [ 21.8%] Processing message   96/441 - 660 points
   📊 [ 22.0%] Processing message   97/441 - 655 points
   📊 [ 22.2%] Processing message   98/441 - 705 points
   📊 [ 22.4%] Processing message   99/441 - 698 points
   📊 [ 22.7%] Processing message  100/441 - 637 points
   📊 [ 22.9%] Processing message  101/441 - 726 points
   📊 [ 23.1%] Processing message  102/441 - 690 points
   📊 [ 23.4%] Processing message  103/441 - 700 points
   📊 [ 23.6%] Processing message  104/441 - 698 points
   📊 [ 23.8%] Processing message  105/441 - 703 points
   📊 [ 24.0%] Processing message  106/441 - 692 points
   📊 [ 24.3%] Processing message  107/441 - 683 points
   📊 [ 24.5%] Processing message  108/441 - 712 points
   📊 [ 24.7%] Processing message  109/441 - 708 points
   📊 [███████░░░░░░░░░░░░░░░░░░░░░░░]  24.9% | Msg  110/441 | 647 pts | ETA: 00:00
       ⚡ Processing rate: 825,017 points/sec | Elapsed: 00:00
   📊 [ 25.2%] Processing message  111/441 - 663 points
   📊 [ 25.4%] Processing message  112/441 - 717 points
   📊 [ 25.6%] Processing message  113/441 - 708 points
   📊 [ 25.9%] Processing message  114/441 - 719 points
   📊 [ 26.1%] Processing message  115/441 - 702 points
   📊 [ 26.3%] Processing message  116/441 - 709 points
   📊 [ 26.5%] Processing message  117/441 - 714 points
   📊 [ 26.8%] Processing message  118/441 - 740 points
   📊 [ 27.0%] Processing message  119/441 - 688 points
   📊 [ 27.2%] Processing message  120/441 - 653 points
   📊 [ 27.4%] Processing message  121/441 - 726 points
   📊 [ 27.7%] Processing message  122/441 - 692 points
   📊 [ 27.9%] Processing message  123/441 - 699 points
   📊 [ 28.1%] Processing message  124/441 - 682 points
   📊 [ 28.3%] Processing message  125/441 - 690 points
   📊 [ 28.6%] Processing message  126/441 - 710 points
   📊 [ 28.8%] Processing message  127/441 - 713 points
   📊 [ 29.0%] Processing message  128/441 - 706 points
   📊 [ 29.3%] Processing message  129/441 - 713 points
   📊 [ 29.5%] Processing message  130/441 - 674 points
   📊 [ 29.7%] Processing message  131/441 - 697 points
   📊 [████████░░░░░░░░░░░░░░░░░░░░░░]  29.9% | Msg  132/441 | 659 pts | ETA: 00:00
       ⚡ Processing rate: 826,258 points/sec | Elapsed: 00:00
   📊 [ 30.2%] Processing message  133/441 - 672 points
   📊 [ 30.4%] Processing message  134/441 - 659 points
   📊 [ 30.6%] Processing message  135/441 - 687 points
   📊 [ 30.8%] Processing message  136/441 - 678 points
   📊 [ 31.1%] Processing message  137/441 - 703 points
   📊 [ 31.3%] Processing message  138/441 - 692 points
   📊 [ 31.5%] Processing message  139/441 - 722 points
   📊 [ 31.7%] Processing message  140/441 - 674 points
   📊 [ 32.0%] Processing message  141/441 - 696 points
   📊 [ 32.2%] Processing message  142/441 - 722 points
   📊 [ 32.4%] Processing message  143/441 - 694 points
   📊 [ 32.7%] Processing message  144/441 - 730 points
   📊 [ 32.9%] Processing message  145/441 - 703 points
   📊 [ 33.1%] Processing message  146/441 - 694 points
   📊 [ 33.3%] Processing message  147/441 - 676 points
   📊 [ 33.6%] Processing message  148/441 - 678 points
   📊 [ 33.8%] Processing message  149/441 - 689 points
   📊 [ 34.0%] Processing message  150/441 - 622 points
   📊 [ 34.2%] Processing message  151/441 - 745 points
   📊 [ 34.5%] Processing message  152/441 - 715 points
   📊 [ 34.7%] Processing message  153/441 - 654 points
   📊 [██████████░░░░░░░░░░░░░░░░░░░░]  34.9% | Msg  154/441 | 696 pts | ETA: 00:00
       ⚡ Processing rate: 828,606 points/sec | Elapsed: 00:00
   📊 [ 35.1%] Processing message  155/441 - 690 points
   📊 [ 35.4%] Processing message  156/441 - 678 points
   📊 [ 35.6%] Processing message  157/441 - 704 points
   📊 [ 35.8%] Processing message  158/441 - 705 points
   📊 [ 36.1%] Processing message  159/441 - 702 points
   📊 [ 36.3%] Processing message  160/441 - 682 points
   📊 [ 36.5%] Processing message  161/441 - 770 points
   📊 [ 36.7%] Processing message  162/441 - 744 points
   📊 [ 37.0%] Processing message  163/441 - 667 points
   📊 [ 37.2%] Processing message  164/441 - 735 points
   📊 [ 37.4%] Processing message  165/441 - 736 points
   📊 [ 37.6%] Processing message  166/441 - 679 points
   📊 [ 37.9%] Processing message  167/441 - 726 points
   📊 [ 38.1%] Processing message  168/441 - 679 points
   📊 [ 38.3%] Processing message  169/441 - 673 points
   📊 [ 38.5%] Processing message  170/441 - 634 points
   📊 [ 38.8%] Processing message  171/441 - 743 points
   📊 [ 39.0%] Processing message  172/441 - 707 points
   📊 [ 39.2%] Processing message  173/441 - 692 points
   📊 [ 39.5%] Processing message  174/441 - 708 points
   📊 [ 39.7%] Processing message  175/441 - 675 points
   📊 [███████████░░░░░░░░░░░░░░░░░░░]  39.9% | Msg  176/441 | 723 pts | ETA: 00:00
       ⚡ Processing rate: 827,161 points/sec | Elapsed: 00:00
   📊 [ 40.1%] Processing message  177/441 - 700 points
   📊 [ 40.4%] Processing message  178/441 - 696 points
   📊 [ 40.6%] Processing message  179/441 - 717 points
   📊 [ 40.8%] Processing message  180/441 - 721 points
   📊 [ 41.0%] Processing message  181/441 - 717 points
   📊 [ 41.3%] Processing message  182/441 - 663 points
   📊 [ 41.5%] Processing message  183/441 - 681 points
   📊 [ 41.7%] Processing message  184/441 - 663 points
   📊 [ 42.0%] Processing message  185/441 - 653 points
   📊 [ 42.2%] Processing message  186/441 - 658 points
   📊 [ 42.4%] Processing message  187/441 - 665 points
   📊 [ 42.6%] Processing message  188/441 - 670 points
   📊 [ 42.9%] Processing message  189/441 - 701 points
   📊 [ 43.1%] Processing message  190/441 - 663 points
   📊 [ 43.3%] Processing message  191/441 - 692 points
   📊 [ 43.5%] Processing message  192/441 - 688 points
   📊 [ 43.8%] Processing message  193/441 - 697 points
   📊 [ 44.0%] Processing message  194/441 - 690 points
   📊 [ 44.2%] Processing message  195/441 - 672 points
   📊 [ 44.4%] Processing message  196/441 - 728 points
   📊 [ 44.7%] Processing message  197/441 - 718 points
   📊 [█████████████░░░░░░░░░░░░░░░░░]  44.9% | Msg  198/441 | 699 pts | ETA: 00:00
       ⚡ Processing rate: 827,142 points/sec | Elapsed: 00:00
   📊 [ 45.1%] Processing message  199/441 - 715 points
   📊 [ 45.4%] Processing message  200/441 - 679 points
   📊 [ 45.6%] Processing message  201/441 - 718 points
   📊 [ 45.8%] Processing message  202/441 - 702 points
   📊 [ 46.0%] Processing message  203/441 - 701 points
   📊 [ 46.3%] Processing message  204/441 - 698 points
   📊 [ 46.5%] Processing message  205/441 - 681 points
   📊 [ 46.7%] Processing message  206/441 - 670 points
   📊 [ 46.9%] Processing message  207/441 - 669 points
   📊 [ 47.2%] Processing message  208/441 - 674 points
   📊 [ 47.4%] Processing message  209/441 - 690 points
   📊 [ 47.6%] Processing message  210/441 - 672 points
   📊 [ 47.8%] Processing message  211/441 - 717 points
   📊 [ 48.1%] Processing message  212/441 - 689 points
   📊 [ 48.3%] Processing message  213/441 - 690 points
   📊 [ 48.5%] Processing message  214/441 - 713 points
   📊 [ 48.8%] Processing message  215/441 - 647 points
   📊 [ 49.0%] Processing message  216/441 - 717 points
   📊 [ 49.2%] Processing message  217/441 - 705 points
   📊 [ 49.4%] Processing message  218/441 - 693 points
   📊 [ 49.7%] Processing message  219/441 - 692 points
   📊 [██████████████░░░░░░░░░░░░░░░░]  49.9% | Msg  220/441 | 696 pts | ETA: 00:00
       ⚡ Processing rate: 826,921 points/sec | Elapsed: 00:00
   📊 [ 50.1%] Processing message  221/441 - 665 points
   📊 [ 50.3%] Processing message  222/441 - 693 points
   📊 [ 50.6%] Processing message  223/441 - 674 points
   📊 [ 50.8%] Processing message  224/441 - 660 points
   📊 [ 51.0%] Processing message  225/441 - 696 points
   📊 [ 51.2%] Processing message  226/441 - 691 points
   📊 [ 51.5%] Processing message  227/441 - 692 points
   📊 [ 51.7%] Processing message  228/441 - 673 points
   📊 [ 51.9%] Processing message  229/441 - 694 points
   📊 [ 52.2%] Processing message  230/441 - 697 points
   📊 [ 52.4%] Processing message  231/441 - 728 points
   📊 [ 52.6%] Processing message  232/441 - 707 points
   📊 [ 52.8%] Processing message  233/441 - 686 points
   📊 [ 53.1%] Processing message  234/441 - 657 points
   📊 [ 53.3%] Processing message  235/441 - 684 points
   📊 [ 53.5%] Processing message  236/441 - 689 points
   📊 [ 53.7%] Processing message  237/441 - 696 points
   📊 [ 54.0%] Processing message  238/441 - 686 points
   📊 [ 54.2%] Processing message  239/441 - 712 points
   📊 [ 54.4%] Processing message  240/441 - 695 points
   📊 [ 54.6%] Processing message  241/441 - 696 points
   📊 [████████████████░░░░░░░░░░░░░░]  54.9% | Msg  242/441 | 714 pts | ETA: 00:00
       ⚡ Processing rate: 829,868 points/sec | Elapsed: 00:00
   📊 [ 55.1%] Processing message  243/441 - 709 points
   📊 [ 55.3%] Processing message  244/441 - 709 points
   📊 [ 55.6%] Processing message  245/441 - 674 points
   📊 [ 55.8%] Processing message  246/441 - 690 points
   📊 [ 56.0%] Processing message  247/441 - 661 points
   📊 [ 56.2%] Processing message  248/441 - 687 points
   📊 [ 56.5%] Processing message  249/441 - 656 points
   📊 [ 56.7%] Processing message  250/441 - 696 points
   📊 [ 56.9%] Processing message  251/441 - 678 points
   📊 [ 57.1%] Processing message  252/441 - 722 points
   📊 [ 57.4%] Processing message  253/441 - 692 points
   📊 [ 57.6%] Processing message  254/441 - 694 points
   📊 [ 57.8%] Processing message  255/441 - 699 points
   📊 [ 58.0%] Processing message  256/441 - 707 points
   📊 [ 58.3%] Processing message  257/441 - 711 points
   📊 [ 58.5%] Processing message  258/441 - 696 points
   📊 [ 58.7%] Processing message  259/441 - 696 points
   📊 [ 59.0%] Processing message  260/441 - 698 points
   📊 [ 59.2%] Processing message  261/441 - 689 points
   📊 [ 59.4%] Processing message  262/441 - 757 points
   📊 [ 59.6%] Processing message  263/441 - 685 points
   📊 [█████████████████░░░░░░░░░░░░░]  59.9% | Msg  264/441 | 765 pts | ETA: 00:00
       ⚡ Processing rate: 830,236 points/sec | Elapsed: 00:00
   📊 [ 60.1%] Processing message  265/441 - 694 points
   📊 [ 60.3%] Processing message  266/441 - 669 points
   📊 [ 60.5%] Processing message  267/441 - 665 points
   📊 [ 60.8%] Processing message  268/441 - 682 points
   📊 [ 61.0%] Processing message  269/441 - 665 points
   📊 [ 61.2%] Processing message  270/441 - 656 points
   📊 [ 61.5%] Processing message  271/441 - 632 points
   📊 [ 61.7%] Processing message  272/441 - 679 points
   📊 [ 61.9%] Processing message  273/441 - 643 points
   📊 [ 62.1%] Processing message  274/441 - 684 points
   📊 [ 62.4%] Processing message  275/441 - 632 points
   📊 [ 62.6%] Processing message  276/441 - 674 points
   📊 [ 62.8%] Processing message  277/441 - 671 points
   📊 [ 63.0%] Processing message  278/441 - 669 points
   📊 [ 63.3%] Processing message  279/441 - 642 points
   📊 [ 63.5%] Processing message  280/441 - 669 points
   📊 [ 63.7%] Processing message  281/441 - 690 points
   📊 [ 63.9%] Processing message  282/441 - 672 points
   📊 [ 64.2%] Processing message  283/441 - 697 points
   📊 [ 64.4%] Processing message  284/441 - 677 points
   📊 [ 64.6%] Processing message  285/441 - 705 points
   📊 [███████████████████░░░░░░░░░░░]  64.9% | Msg  286/441 | 720 pts | ETA: 00:00
       ⚡ Processing rate: 831,129 points/sec | Elapsed: 00:00
   📊 [ 65.1%] Processing message  287/441 - 709 points
   📊 [ 65.3%] Processing message  288/441 - 722 points
   📊 [ 65.5%] Processing message  289/441 - 725 points
   📊 [ 65.8%] Processing message  290/441 - 732 points
   📊 [ 66.0%] Processing message  291/441 - 303 points
   📊 [ 66.2%] Processing message  292/441 - 866 points
   📊 [ 66.4%] Processing message  293/441 - 735 points
   📊 [ 66.7%] Processing message  294/441 - 768 points
   📊 [ 66.9%] Processing message  295/441 - 741 points
   📊 [ 67.1%] Processing message  296/441 - 745 points
   📊 [ 67.3%] Processing message  297/441 - 716 points
   📊 [ 67.6%] Processing message  298/441 - 714 points
   📊 [ 67.8%] Processing message  299/441 - 685 points
   📊 [ 68.0%] Processing message  300/441 - 688 points
   📊 [ 68.3%] Processing message  301/441 - 669 points
   📊 [ 68.5%] Processing message  302/441 - 665 points
   📊 [ 68.7%] Processing message  303/441 - 678 points
   📊 [ 68.9%] Processing message  304/441 - 662 points
   📊 [ 69.2%] Processing message  305/441 - 721 points
   📊 [ 69.4%] Processing message  306/441 - 690 points
   📊 [ 69.6%] Processing message  307/441 - 708 points
   📊 [████████████████████░░░░░░░░░░]  69.8% | Msg  308/441 | 671 pts | ETA: 00:00
       ⚡ Processing rate: 831,078 points/sec | Elapsed: 00:00
   📊 [ 70.1%] Processing message  309/441 - 712 points
   📊 [ 70.3%] Processing message  310/441 - 693 points
   📊 [ 70.5%] Processing message  311/441 - 679 points
   📊 [ 70.7%] Processing message  312/441 - 703 points
   📊 [ 71.0%] Processing message  313/441 - 715 points
   📊 [ 71.2%] Processing message  314/441 - 768 points
   📊 [ 71.4%] Processing message  315/441 - 760 points
   📊 [ 71.7%] Processing message  316/441 - 798 points
   📊 [ 71.9%] Processing message  317/441 - 779 points
   📊 [ 72.1%] Processing message  318/441 - 804 points
   📊 [ 72.3%] Processing message  319/441 - 757 points
   📊 [ 72.6%] Processing message  320/441 - 814 points
   📊 [ 72.8%] Processing message  321/441 - 774 points
   📊 [ 73.0%] Processing message  322/441 - 796 points
   📊 [ 73.2%] Processing message  323/441 - 798 points
   📊 [ 73.5%] Processing message  324/441 - 758 points
   📊 [ 73.7%] Processing message  325/441 - 795 points
   📊 [ 73.9%] Processing message  326/441 - 793 points
   📊 [ 74.1%] Processing message  327/441 - 779 points
   📊 [ 74.4%] Processing message  328/441 - 804 points
   📊 [ 74.6%] Processing message  329/441 - 790 points
   📊 [██████████████████████░░░░░░░░]  74.8% | Msg  330/441 | 769 pts | ETA: 00:00
       ⚡ Processing rate: 832,869 points/sec | Elapsed: 00:00
   📊 [ 75.1%] Processing message  331/441 - 786 points
   📊 [ 75.3%] Processing message  332/441 - 736 points
   📊 [ 75.5%] Processing message  333/441 - 731 points
   📊 [ 75.7%] Processing message  334/441 - 703 points
   📊 [ 76.0%] Processing message  335/441 - 669 points
   📊 [ 76.2%] Processing message  336/441 - 745 points
   📊 [ 76.4%] Processing message  337/441 - 748 points
   📊 [ 76.6%] Processing message  338/441 - 823 points
   📊 [ 76.9%] Processing message  339/441 - 826 points
   📊 [ 77.1%] Processing message  340/441 - 838 points
   📊 [ 77.3%] Processing message  341/441 - 795 points
   📊 [ 77.6%] Processing message  342/441 - 817 points
   📊 [ 77.8%] Processing message  343/441 - 842 points
   📊 [ 78.0%] Processing message  344/441 - 789 points
   📊 [ 78.2%] Processing message  345/441 - 757 points
   📊 [ 78.5%] Processing message  346/441 - 747 points
   📊 [ 78.7%] Processing message  347/441 - 771 points
   📊 [ 78.9%] Processing message  348/441 - 786 points
   📊 [ 79.1%] Processing message  349/441 - 809 points
   📊 [ 79.4%] Processing message  350/441 - 770 points
   📊 [ 79.6%] Processing message  351/441 - 748 points
   📊 [███████████████████████░░░░░░░]  79.8% | Msg  352/441 | 722 pts | ETA: 00:00
       ⚡ Processing rate: 835,508 points/sec | Elapsed: 00:00
   📊 [ 80.0%] Processing message  353/441 - 725 points
   📊 [ 80.3%] Processing message  354/441 - 723 points
   📊 [ 80.5%] Processing message  355/441 - 735 points
   📊 [ 80.7%] Processing message  356/441 - 769 points
   📊 [ 81.0%] Processing message  357/441 - 818 points
   📊 [ 81.2%] Processing message  358/441 - 812 points
   📊 [ 81.4%] Processing message  359/441 - 843 points
   📊 [ 81.6%] Processing message  360/441 - 810 points
   📊 [ 81.9%] Processing message  361/441 - 833 points
   📊 [ 82.1%] Processing message  362/441 - 826 points
   📊 [ 82.3%] Processing message  363/441 - 825 points
   📊 [ 82.5%] Processing message  364/441 - 798 points
   📊 [ 82.8%] Processing message  365/441 - 820 points
   📊 [ 83.0%] Processing message  366/441 - 790 points
   📊 [ 83.2%] Processing message  367/441 - 838 points
   📊 [ 83.4%] Processing message  368/441 - 807 points
   📊 [ 83.7%] Processing message  369/441 - 742 points
   📊 [ 83.9%] Processing message  370/441 - 766 points
   📊 [ 84.1%] Processing message  371/441 - 698 points
   📊 [ 84.4%] Processing message  372/441 - 684 points
   📊 [ 84.6%] Processing message  373/441 - 682 points
   📊 [█████████████████████████░░░░░]  84.8% | Msg  374/441 | 689 pts | ETA: 00:00
       ⚡ Processing rate: 835,305 points/sec | Elapsed: 00:00
   📊 [ 85.0%] Processing message  375/441 - 696 points
   📊 [ 85.3%] Processing message  376/441 - 694 points
   📊 [ 85.5%] Processing message  377/441 - 708 points
   📊 [ 85.7%] Processing message  378/441 - 706 points
   📊 [ 85.9%] Processing message  379/441 - 693 points
   📊 [ 86.2%] Processing message  380/441 - 672 points
   📊 [ 86.4%] Processing message  381/441 - 676 points
   📊 [ 86.6%] Processing message  382/441 - 694 points
   📊 [ 86.8%] Processing message  383/441 - 667 points
   📊 [ 87.1%] Processing message  384/441 - 660 points
   📊 [ 87.3%] Processing message  385/441 - 645 points
   📊 [ 87.5%] Processing message  386/441 - 608 points
   📊 [ 87.8%] Processing message  387/441 - 641 points
   📊 [ 88.0%] Processing message  388/441 - 654 points
   📊 [ 88.2%] Processing message  389/441 - 638 points
   📊 [ 88.4%] Processing message  390/441 - 696 points
   📊 [ 88.7%] Processing message  391/441 - 659 points
   📊 [ 88.9%] Processing message  392/441 - 691 points
   📊 [ 89.1%] Processing message  393/441 - 702 points
   📊 [ 89.3%] Processing message  394/441 - 697 points
   📊 [ 89.6%] Processing message  395/441 - 665 points
   📊 [██████████████████████████░░░░]  89.8% | Msg  396/441 | 643 pts | ETA: 00:00
       ⚡ Processing rate: 835,997 points/sec | Elapsed: 00:00
   📊 [ 90.0%] Processing message  397/441 - 672 points
   📊 [ 90.2%] Processing message  398/441 - 635 points
   📊 [ 90.5%] Processing message  399/441 - 642 points
   📊 [ 90.7%] Processing message  400/441 - 624 points
   📊 [ 90.9%] Processing message  401/441 - 679 points
   📊 [ 91.2%] Processing message  402/441 - 636 points
   📊 [ 91.4%] Processing message  403/441 - 589 points
   📊 [ 91.6%] Processing message  404/441 - 600 points
   📊 [ 91.8%] Processing message  405/441 - 609 points
   📊 [ 92.1%] Processing message  406/441 - 608 points
   📊 [ 92.3%] Processing message  407/441 - 616 points
   📊 [ 92.5%] Processing message  408/441 - 613 points
   📊 [ 92.7%] Processing message  409/441 - 646 points
   📊 [ 93.0%] Processing message  410/441 - 592 points
   📊 [ 93.2%] Processing message  411/441 - 465 points
   📊 [ 93.4%] Processing message  412/441 - 762 points
   📊 [ 93.7%] Processing message  413/441 - 669 points
   📊 [ 93.9%] Processing message  414/441 - 650 points
   📊 [ 94.1%] Processing message  415/441 - 626 points
   📊 [ 94.3%] Processing message  416/441 - 655 points
   📊 [ 94.6%] Processing message  417/441 - 619 points
   📊 [████████████████████████████░░]  94.8% | Msg  418/441 | 664 pts | ETA: 00:00
       ⚡ Processing rate: 833,763 points/sec | Elapsed: 00:00
   📊 [ 95.0%] Processing message  419/441 - 605 points
   📊 [ 95.2%] Processing message  420/441 - 582 points
   📊 [ 95.5%] Processing message  421/441 - 605 points
   📊 [ 95.7%] Processing message  422/441 - 615 points
   📊 [ 95.9%] Processing message  423/441 - 632 points
   📊 [ 96.1%] Processing message  424/441 - 639 points
   📊 [ 96.4%] Processing message  425/441 - 652 points
   📊 [ 96.6%] Processing message  426/441 - 637 points
   📊 [ 96.8%] Processing message  427/441 - 629 points
   📊 [ 97.1%] Processing message  428/441 - 665 points
   📊 [ 97.3%] Processing message  429/441 - 639 points
   📊 [ 97.5%] Processing message  430/441 - 670 points
   📊 [ 97.7%] Processing message  431/441 - 635 points
   📊 [ 98.0%] Processing message  432/441 - 637 points
   📊 [ 98.2%] Processing message  433/441 - 629 points
   📊 [ 98.4%] Processing message  434/441 - 619 points
   📊 [ 98.6%] Processing message  435/441 - 626 points
   📊 [ 98.9%] Processing message  436/441 - 635 points
   📊 [ 99.1%] Processing message  437/441 - 619 points
   📊 [ 99.3%] Processing message  438/441 - 631 points
   📊 [ 99.5%] Processing message  439/441 - 660 points
   📊 [█████████████████████████████░]  99.8% | Msg  440/441 | 683 pts | ETA: 00:00
       ⚡ Processing rate: 833,776 points/sec | Elapsed: 00:00
   📊 [██████████████████████████████] 100.0% | Msg  441/441 | 607 pts | ETA: 00:00
       ⚡ Processing rate: 834,017 points/sec | Elapsed: 00:00

   🏁 Message processing completed in 00:00
   ⚡ Average processing rate: 834,981 points/sec

🔢 CONVERTING TO NUMPY ARRAYS...
   🔄 Converting X coordinates...
   ✅ X coordinates converted (306,106 points)
   🔍 Debug - X array stats: min=-7.857010, max=13.419770
   🔄 Converting Y coordinates...
   ✅ Y coordinates converted (306,106 points)
   🔍 Debug - Y array stats: min=-3.257249, max=4.898147
   🔄 Converting Z coordinates...
   ✅ Z coordinates converted (306,106 points)
   🔍 Debug - Z array stats: min=-1.388804, max=10.151234
   🔍 Debug - Original list sizes: x=306106, y=306106, z=306106
   🔍 Debug - First 3 points from lists:
      Point 0: (0.885330, -2.294670, 2.135929)
      Point 1: (-1.255601, 4.305957, 3.777949)
      Point 2: (-1.601313, 4.293988, 4.085413)
   🔄 Converting intensity values...
   ✅ Intensity values converted (306,106 points)
   🔄 Converting GPS time values...
   ✅ GPS time values converted (306,106 points)
   ⏱️  Array conversion completed in 0.05 seconds
   💾 Memory usage: ~7.0 MB for coordinates

🔍 DATA QUALITY ANALYSIS:
--------------------------------------------------
📍 Coordinate ranges:
   • X:    -7.857010 to    13.419770 (range:  21.276781)
   • Y:    -3.257249 to     4.898147 (range:   8.155396)
   • Z:    -1.388804 to    10.151234 (range:  11.540038)

🧪 Data integrity:
   • NaN values - X: 0, Y: 0, Z: 0
   • Inf values - X: 0, Y: 0, Z: 0
   • Zero values - X: 0, Y: 0, Z: 0
   • Total points before filtering: 306,106
   • Extremely small values - X: 0, Y: 0, Z: 0
   • Points near origin (0,0,0): 0
✅ All coordinate values are valid

📁 CREATING LAS FILE...
--------------------------------------------------
🎯 Output file: ./12_2025-09-17-16-31-50.las
🔧 Using point format: 1
   📋 Format 1 supports: XYZ + GPS time + intensity
⚙️  Setting coordinate data...
⚙️  Processing intensity data...
   • Original intensity range: 0.000 to 170.000
   • Unique intensity values: 17,844
   • Scaled from [0,255] to [0,65535]
   ✅ Intensity data added successfully
⚙️  Processing GPS time data...
   • GPS time array length: 306,106
   • GPS time data type: float64
   • GPS time range: 1758115910.764340 to 1758115954.759777
   • Unique GPS time values: 441
   🎨 Creating sequential time for better visualization...
   • Sequential time created: 1758115910.764340 to 1758115954.759777
   • Time step: 0.000144 s
   • Min time difference: 0.000144 s
   • Max time difference: 0.000144 s
   • Average time difference: 0.000144 s
   • Median time difference: 0.000144 s
   • Time is monotonically increasing: True
   • First 10 GPS time values: [1.75811591e+09 1.75811591e+09 1.75811591e+09 1.75811591e+09
 1.75811591e+09 1.75811591e+09 1.75811591e+09 1.75811591e+09
 1.75811591e+09 1.75811591e+09]
   • Last 10 GPS time values: [1.75811595e+09 1.75811595e+09 1.75811595e+09 1.75811595e+09
 1.75811595e+09 1.75811595e+09 1.75811595e+09 1.75811595e+09
 1.75811595e+09 1.75811595e+09]
   • Total time span: 43.995437 seconds (0.73 minutes)
   🎨 Perfect for temporal visualization - each point has unique time
⚙️  Processing GPS time data...
   • GPS time array length: 306,106
   • GPS time data type: float64
   • GPS time range: 1758115910.764340 to 1758115954.759777
   • Unique GPS time values: 306,106
   • Min time difference: 0.000144 s
   • Max time difference: 0.000144 s
   • Average time difference: 0.000144 s
   • Median time difference: 0.000144 s
   • Time is monotonically increasing: True
   • First 10 GPS time values: [1.75811591e+09 1.75811591e+09 1.75811591e+09 1.75811591e+09
 1.75811591e+09 1.75811591e+09 1.75811591e+09 1.75811591e+09
 1.75811591e+09 1.75811591e+09]
   • Last 10 GPS time values: [1.75811595e+09 1.75811595e+09 1.75811595e+09 1.75811595e+09
 1.75811595e+09 1.75811595e+09 1.75811595e+09 1.75811595e+09
 1.75811595e+09 1.75811595e+09]
   • Total time span: 43.995437 seconds (0.73 minutes)
   • Estimated scan duration: 44.1 seconds
   • Time span vs estimated: 44.0s vs 44.1s
   ℹ️  GPS time appears to be Unix timestamp
   🔄 Converting Unix timestamp to GPS time...
   • GPS time after conversion: 1442151110.764340 to 1442151154.759777
   ✅ GPS time data assigned to LAS file
   ✅ Verified GPS time in LAS: 1442151110.764340 to 1442151154.759777
   ✅ Unique time values in LAS: 306,106
   ✅ GPS time successfully added to LAS file
   ✅ Each point has unique timestamp
⚙️  Setting LAS header parameters...
   • Offset: [-7.857010, -3.257249, -1.388804]
   • Scale: [0.001, 0.001, 0.001]
   ℹ️  No RGB data (point cloud contains no color information)

💾 WRITING LAS FILE...
   ⏱️  File write completed in 0.02 seconds

🧭 СОЗДАНИЕ .POS ФАЙЛА...
--------------------------------------------------
📡 Источник: топик '/mavros/local_position/odom'
🎯 Выходной файл: ./12_2025-09-17-16-31-50.pos
🔄 Извлечение данных одометрии...
   📊 Всего сообщений одометрии: 2,633
   📊 [  0.0%] Обработано 1/2,633 сообщений
   📊 [  0.1%] Обработано 2/2,633 сообщений
   📊 [  0.1%] Обработано 3/2,633 сообщений
   📊 [  0.2%] Обработано 4/2,633 сообщений
   📊 [  0.2%] Обработано 5/2,633 сообщений
   📊 [  5.0%] Обработано 131/2,633 сообщений
   📊 [ 10.0%] Обработано 262/2,633 сообщений
   📊 [ 14.9%] Обработано 393/2,633 сообщений
   📊 [ 19.9%] Обработано 524/2,633 сообщений
   📊 [ 24.9%] Обработано 655/2,633 сообщений
   📊 [ 29.9%] Обработано 786/2,633 сообщений
   📊 [ 34.8%] Обработано 917/2,633 сообщений
   📊 [ 39.8%] Обработано 1,048/2,633 сообщений
   📊 [ 44.8%] Обработано 1,179/2,633 сообщений
   📊 [ 49.8%] Обработано 1,310/2,633 сообщений
   📊 [ 54.7%] Обработано 1,441/2,633 сообщений
   📊 [ 59.7%] Обработано 1,572/2,633 сообщений
   📊 [ 64.7%] Обработано 1,703/2,633 сообщений
   📊 [ 69.7%] Обработано 1,834/2,633 сообщений
   📊 [ 74.6%] Обработано 1,965/2,633 сообщений
   📊 [ 79.6%] Обработано 2,096/2,633 сообщений
   📊 [ 84.6%] Обработано 2,227/2,633 сообщений
   📊 [ 89.6%] Обработано 2,358/2,633 сообщений
   📊 [ 94.5%] Обработано 2,489/2,633 сообщений
   📊 [ 99.5%] Обработано 2,620/2,633 сообщений
   ⏱️  Извлечение завершено за 0.09 секунд

📊 АНАЛИЗ ТРАЕКТОРИИ:
   • Точек траектории: 2,633
   • Временной диапазон: 43.93 секунд
   • Средняя частота: 59.9 Hz
   • Общая дистанция: 6.55 м
   • Макс. шаг: 0.014 м
   • Средний шаг: 0.002 м
   • Диапазон X: -0.816587 до -0.005998
   • Диапазон Y: -0.158388 до 0.319677
   • Диапазон Z: -0.260892 до 0.270503
🔄 Конвертация кватернионов в углы Эйлера...
   • Диапазон Roll: -6.12° до 7.07°
   • Диапазон Pitch: -3.95° до 9.53°
   • Диапазон Yaw: -180.00° до 179.99°

💾 ЗАПИСЬ .POS ФАЙЛА...
✅ .POS файл создан успешно!
   📁 Файл: ./12_2025-09-17-16-31-50.pos
   📊 Размер: 195,715 байт
   🔢 Записей: 2,633
   ✅ Проверка: 2633 строк данных
   🔍 Первая запись: 1758115910.852247 -0.019972 0.142210 -0.255183 0.023871 0.070827 1.872394
   🔍 Последняя запись: 1758115954.783838 -0.395848 -0.032071 -0.010227 0.695535 1.752346 179.725807

🎉 SUCCESS! LAS FILE CREATED
==================================================
📁 File: ./12_2025-09-17-16-31-50.las
📊 Size: 8,571,343 bytes (8.17 MB)
🔢 Points: 306,106
📏 Point format: 1
🗂️  LAS version: 1.4
🧭 POS file: ./12_2025-09-17-16-31-50.pos
📊 POS size: 195,715 bytes

✅ FILE VERIFICATION:
   • Points in file: 306,106
   • Coordinate ranges verified:
     - X: -7.860010 to 13.419990
     - Y: -3.260249 to 4.899751
     - Z: -1.389804 to 10.150196
   • Intensity verified: 0 - 43690
⚡ Intensity: ✅ Range 0.000 - 170.000
   • GPS time verified: 1442151110.764340 - 1442151154.759777
   • GPS time unique values: 306,106
⏰ GPS time: ✅ Range 1442151110.764340 - 1442151154.759777
   • Temporal density: 6958 points/second
   🎨 Ready for temporal visualization in CloudCompare!
   ✅ LAS file is valid and ready for use

✅ Файл обработан за 00:29

🏁 ОБРАБОТКА ДИРЕКТОРИИ ЗАВЕРШЕНА!
================================================================================
⏱️  Общее время: 00:29
✅ Успешно обработано: 1/1 файлов
📊 Среднее время на файл: 29.6 секунд

🎉 ПРОГРАММА ЗАВЕРШЕНА УСПЕШНО!
(base) devitt@devitts-MacBook-Pro rosbag_to_las % 