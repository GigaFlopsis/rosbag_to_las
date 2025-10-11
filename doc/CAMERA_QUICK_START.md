# Извлечение Позиций Камеры - Краткое Руководство

## 🎯 Быстрый старт

Извлечь позиции камеры из ROS bag файла в формате для фотограмметрии:

```bash
python3 extract_camera_positions.py
```

## 📦 Что делает скрипт

Извлекает из bag файла:
- ⏱️ Точное время съёмки каждого кадра
- 📝 Имена файлов фотографий  
- 📍 Позицию дрона (x, y, z) с интерполяцией
- 🧭 Ориентацию (quaternion)

## 📊 Форматы вывода

| Формат | Использование |
|--------|---------------|
| **CSV** | Excel, универсальный импорт |
| **JSON** | Программная обработка |
| **Agisoft TXT** | Agisoft Metashape, Pix4D |

## 🚀 Быстрый тест

```bash
# Автоматический тест на test.bag
python3 test_camera_extract.py
```

**Создаёт файлы:**
- `test_camera_positions.csv`
- `test_camera_positions.json`
- `test_camera_positions_agisoft.txt`

## 📝 Пример вывода

### CSV формат:
```csv
timestamp,seq_id,filename,x,y,z,qx,qy,qz,qw
1758293459.946,1000,image_20250919_175100_691924_seq1000.jpg,-0.018,0.137,-0.025,-0.040,0.014,0.048,-0.998
```

### Agisoft TXT формат:
```
image_20250919_175100_691924_seq1000.jpg -0.018345 0.137097 -0.025323 -0.040433 0.013860 0.048478 -0.997909
```

## 🔧 Требуемые топики

Скрипт автоматически использует:
- `/mavros/cam_imu_sync/cam_imu_stamp` - метки времени кадров
- `/mavros/statustext/send` - имена файлов (фильтр `[PHOTO]:`)
- `/mavros/local_position/odom` - позиция и ориентация

## 📖 Подробная документация

См. [CAMERA_POSITIONS_EXTRACTOR.md](./CAMERA_POSITIONS_EXTRACTOR.md)

## 🐛 Отладка

Для анализа структуры сообщений перед извлечением:

```bash
python3 camera_frames_debug.py
```

См. [CAMERA_FRAMES_DEBUG_README.md](./CAMERA_FRAMES_DEBUG_README.md)

---

**Часть проекта rosbag_to_las**
