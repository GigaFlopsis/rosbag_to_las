# 📦 Руководство по установке

Это руководство поможет установить `rosbag_to_las` на любой платформе с минимальными усилиями.

## 🎯 Быстрый старт

### Вариант 1: Автоматическая установка (рекомендуется)

#### macOS / Linux:
```bash
chmod +x install.sh
./install.sh
```

#### Windows:
```cmd
install.bat
```

### Вариант 2: Docker (самый простой, работает везде)

```bash
# Сборка контейнера
docker build -t rosbag_to_las .

# Запуск (поместите bag файлы в папку ./data)
docker run -it -v $(pwd)/data:/data rosbag_to_las

# Или через docker-compose
docker-compose up
```

### Вариант 3: Ручная установка

#### Шаг 1: Клонирование репозитория
```bash
git clone https://github.com/eddie3ruff/bag2laz.git
cd bag2laz
```

#### Шаг 2: Создание виртуального окружения (рекомендуется)
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# или
venv\Scripts\activate.bat  # Windows
```

#### Шаг 3: Установка зависимостей

**macOS:**
```bash
pip install -r requirements-macos.txt
```

**Linux (с системным ROS):**
```bash
# Сначала установите ROS Noetic
sudo apt install ros-noetic-desktop-full
source /opt/ros/noetic/setup.bash

# Затем Python пакеты
pip install -r requirements-linux.txt
```

**Linux (без системного ROS) / Windows:**
```bash
pip install -r requirements.txt
```

## 📋 Зависимости по платформам

### Общие зависимости (все платформы)
- `numpy` - математические операции
- `scipy` - научные вычисления
- `scikit-learn` - машинное обучение для SLAM
- `matplotlib` - визуализация
- `laspy` - работа с LAS/LAZ файлами
- `lazrs` - компрессия LAZ (или `laszip` как альтернатива)

### Платформо-специфичные зависимости

#### macOS
ROS пакеты устанавливаются через **rospypi**:
- `rospy`
- `rosbag`
- `sensor_msgs`
- `geometry_msgs`
- `nav_msgs`

#### Linux
**Рекомендуется**: системный ROS Noetic
```bash
sudo apt install ros-noetic-desktop-full
```

Альтернативно: можно использовать rospypi (как на macOS)

#### Windows
ROS пакеты через **rospypi** (поддержка ограничена)
**Рекомендуется**: использовать Docker

## 🐳 Docker - универсальное решение

Docker обеспечивает полную изоляцию и работает одинаково на всех платформах.

### Установка Docker
- **macOS**: [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/install/)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)
- **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)

### Использование

```bash
# Сборка образа (один раз)
docker build -t rosbag_to_las .

# Подготовка данных
mkdir data
cp your_file.bag data/

# Запуск
docker run -it -v $(pwd)/data:/data rosbag_to_las
```

## 🔧 Альтернативные варианты установки

### Использование pip install (когда будет опубликовано)
```bash
# Базовая установка
pip install rosbag_to_las

# macOS с ROS зависимостями
pip install rosbag_to_las[macos]

# С альтернативным LAZ бэкендом
pip install rosbag_to_las[laszip]
```

### Установка из исходников через setup.py
```bash
git clone https://github.com/eddie3ruff/bag2laz.git
cd bag2laz
pip install -e .  # Установка в режиме разработки
```

## ✅ Проверка установки

```bash
# Проверка импорта модулей
python3 -c "import rosbag; import laspy; import numpy; print('✅ Все зависимости установлены!')"

# Запуск приложения
python3 bag2las_transform.py --help
```

## 🆘 Устранение проблем

### Проблема: ROS пакеты не устанавливаются на macOS
**Решение**: Убедитесь, что используете правильный индекс пакетов
```bash
pip install --extra-index-url https://rospypi.github.io/simple/ rosbag
```

### Проблема: Ошибка компиляции lazrs
**Решение**: Используйте альтернативный бэкенд
```bash
pip uninstall lazrs
pip install laszip
```

### Проблема: Конфликт версий на Linux с системным ROS
**Решение**: Не устанавливайте ROS пакеты через pip, используйте системные
```bash
# Убедитесь, что ROS sourced
source /opt/ros/noetic/setup.bash
# Установите только Python библиотеки
pip install numpy scipy scikit-learn matplotlib laspy lazrs
```

### Проблема: Permission denied при запуске install.sh
**Решение**: Сделайте скрипт исполняемым
```bash
chmod +x install.sh
./install.sh
```

## 🌟 Рекомендации по выбору метода установки

| Платформа | Рекомендуемый метод | Альтернатива |
|-----------|---------------------|--------------|
| **macOS** | `install.sh` | Docker |
| **Linux (Ubuntu 20.04)** | `install.sh` + системный ROS | Docker |
| **Windows** | Docker | `install.bat` |
| **Другие Linux** | Docker | `install.sh` |

## 📚 Дополнительные ресурсы

- [README.md](README.md) - Основная документация
- [SLAM_USER_GUIDE.md](doc/SLAM_USER_GUIDE.md) - Руководство по SLAM
- [QUICK_START.md](doc/QUICK_START.md) - Быстрый старт

## 💡 Лучшие практики

1. **Используйте виртуальное окружение** - изолирует зависимости проекта
2. **Docker для продакшена** - гарантирует консистентность
3. **Системный ROS на Linux** - лучшая производительность
4. **rospypi на macOS** - единственный способ без виртуальной машины

## 🔄 Обновление

```bash
# С git
git pull origin main
pip install -r requirements.txt --upgrade

# Через pip (когда будет опубликовано)
pip install --upgrade rosbag_to_las

# Docker
docker build -t rosbag_to_las . --no-cache
```
