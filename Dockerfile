# Docker контейнер для rosbag_to_las
# Полностью изолированная среда со всеми зависимостями

FROM osrf/ros:noetic-desktop-full

# Метаданные
LABEL maintainer="your.email@example.com"
LABEL description="ROS Bag to LAS/LAZ converter with SLAM optimization"
LABEL version="2.0.0"

# Установка Python зависимостей
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-numpy \
    python3-scipy \
    python3-sklearn \
    python3-matplotlib \
    && rm -rf /var/lib/apt/lists/*

# Установка специфичных Python пакетов
RUN pip3 install --no-cache-dir \
    laspy>=2.0.0 \
    lazrs>=0.4.0

# Создание рабочей директории
WORKDIR /workspace

# Копирование скриптов
COPY bag2las.py bag2las_transform.py /workspace/

# Создание директории для данных
RUN mkdir -p /data

# Установка переменных окружения ROS
ENV ROS_DISTRO=noetic
ENV PYTHONPATH=/opt/ros/noetic/lib/python3/dist-packages:$PYTHONPATH

# Точка входа
ENTRYPOINT ["/bin/bash", "-c", "source /opt/ros/noetic/setup.bash && exec \"$@\"", "--"]
CMD ["python3", "bag2las_transform.py"]

# Инструкции по использованию:
# 
# Сборка образа:
#   docker build -t rosbag_to_las .
#
# Запуск интерактивно:
#   docker run -it -v $(pwd)/data:/data rosbag_to_las
#
# Запуск с конкретным bag файлом:
#   docker run -v $(pwd)/data:/data rosbag_to_las python3 bag2las_transform.py /data/your_file.bag
