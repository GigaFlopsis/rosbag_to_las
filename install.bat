@echo off
REM Установщик для Windows

echo 🚀 Установка rosbag_to_las для Windows...
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден. Установите Python 3.6 или выше.
    echo    Скачать: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python найден
python --version
echo.

REM Создание виртуального окружения
set /p CREATEVENV="📦 Создать виртуальное окружение? (y/n, рекомендуется): "
if /i "%CREATEVENV%"=="y" (
    if exist "venv" (
        echo ⚠️  Виртуальное окружение уже существует
    ) else (
        echo 📦 Создание виртуального окружения...
        python -m venv venv
    )
    
    echo 🔧 Активация виртуального окружения...
    call venv\Scripts\activate.bat
)

REM Обновление pip
echo ⬆️  Обновление pip...
python -m pip install --upgrade pip setuptools wheel
echo.

REM Установка зависимостей
echo 📥 Установка зависимостей...
echo    (ROS пакеты будут установлены через rospypi)
python -m pip install -r requirements.txt

echo.
echo ✅ Установка завершена!
echo.
echo 📝 Следующие шаги:
if exist "venv" (
    echo    1. Активируйте виртуальное окружение:
    echo       venv\Scripts\activate.bat
    echo    2. Запустите приложение:
) else (
    echo    1. Запустите приложение:
)
echo       python bag2las_transform.py
echo.
echo 📚 Документация: README.md
echo 🆘 Помощь по SLAM: doc\SLAM_USER_GUIDE.md
echo.
pause
