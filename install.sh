#!/bin/bash
# Автоматический установщик для rosbag_to_las
# Определяет платформу и устанавливает соответствующие зависимости

set -e  # Остановка при ошибках

echo "🚀 Установка rosbag_to_las..."
echo ""

# Определяем операционную систему
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=Linux;;
    Darwin*)    PLATFORM=macOS;;
    *)          PLATFORM="UNKNOWN:${OS}"
esac

echo "🖥️  Обнаружена платформа: $PLATFORM"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.6 или выше."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python версия: $PYTHON_VERSION"
echo ""

# Создание виртуального окружения (рекомендуется)
read -p "📦 Создать виртуальное окружение? (y/n, рекомендуется): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "venv" ]; then
        echo "⚠️  Виртуальное окружение уже существует"
    else
        echo "📦 Создание виртуального окружения..."
        python3 -m venv venv
    fi
    
    echo "🔧 Активация виртуального окружения..."
    source venv/bin/activate
fi

# Обновление pip
echo "⬆️  Обновление pip..."
python3 -m pip install --upgrade pip setuptools wheel
echo ""

# Платформо-специфичная установка
if [ "$PLATFORM" = "macOS" ]; then
    echo "🍎 Установка зависимостей для macOS..."
    echo "   (ROS пакеты будут установлены через rospypi)"
    python3 -m pip install -r requirements-macos.txt
    
elif [ "$PLATFORM" = "Linux" ]; then
    echo "🐧 Установка зависимостей для Linux..."
    
    # Проверка системного ROS
    if [ -f "/opt/ros/noetic/setup.bash" ]; then
        echo "✅ Найден ROS Noetic"
        source /opt/ros/noetic/setup.bash
        python3 -m pip install -r requirements-linux.txt
    else
        echo "⚠️  Системный ROS не найден!"
        echo ""
        echo "Выберите вариант:"
        echo "1) Установить системный ROS Noetic (рекомендуется)"
        echo "2) Использовать ROS через pip (может работать нестабильно)"
        read -p "Ваш выбор (1/2): " -n 1 -r
        echo
        
        if [[ $REPLY = "1" ]]; then
            echo ""
            echo "Установите ROS Noetic:"
            echo "  sudo sh -c 'echo \"deb http://packages.ros.org/ros/ubuntu \$(lsb_release -sc) main\" > /etc/apt/sources.list.d/ros-latest.list'"
            echo "  sudo apt install curl"
            echo "  curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -"
            echo "  sudo apt update"
            echo "  sudo apt install ros-noetic-desktop-full"
            echo ""
            echo "После установки запустите этот скрипт снова."
            exit 0
        else
            echo "Установка через pip..."
            python3 -m pip install -r requirements-macos.txt
        fi
    fi
else
    echo "⚠️  Неизвестная платформа, пробуем установку через pip..."
    python3 -m pip install -r requirements.txt
fi

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📝 Следующие шаги:"
if [ -d "venv" ]; then
    echo "   1. Активируйте виртуальное окружение:"
    echo "      source venv/bin/activate"
    echo "   2. Запустите приложение:"
else
    echo "   1. Запустите приложение:"
fi
echo "      python3 bag2las_transform.py"
echo ""
echo "📚 Документация: README.md"
echo "🆘 Помощь по SLAM: doc/SLAM_USER_GUIDE.md"
