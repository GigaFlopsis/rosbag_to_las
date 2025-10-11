#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Извлечение позиций камеры из ROS bag файла.

Извлекает:
- Метки времени съёмки из /mavros/cam_imu_sync/cam_imu_stamp
- Имена файлов из /mavros/statustext/send (фильтр [PHOTO]:)
- Позиции из /mavros/local_position/odom с интерполяцией

Выходной формат: CSV, JSON, или Agisoft-совместимый TXT
"""

import rosbag
import os
import csv
import json
from datetime import datetime
from collections import defaultdict
import numpy as np
from scipy.interpolate import interp1d


class CameraPositionExtractor:
    """
    Класс для извлечения позиций камеры из ROS bag.
    """
    
    def __init__(self, bag_file):
        """
        Инициализация экстрактора.
        
        Parameters:
            bag_file: Путь к ROS bag файлу
        """
        self.bag_file = bag_file
        self.cam_imu_topic = "/mavros/cam_imu_sync/cam_imu_stamp"
        self.statustext_topic = "/mavros/statustext/send"
        self.odom_topic = "/mavros/local_position/odom"
        
        # Данные
        self.camera_frames = []  # {timestamp, seq_id}
        self.photo_names = {}    # {timestamp: filename}
        self.odometry_data = []  # {timestamp, x, y, z, qx, qy, qz, qw}
        
        # Результаты
        self.camera_positions = []
    
    def extract_data(self):
        """
        Извлечь все необходимые данные из bag файла.
        """
        print("\n" + "=" * 80)
        print("📦 ИЗВЛЕЧЕНИЕ ДАННЫХ ИЗ BAG ФАЙЛА")
        print("=" * 80)
        
        with rosbag.Bag(self.bag_file, 'r') as bag:
            # Проверить наличие топиков
            bag_info = bag.get_type_and_topic_info()
            
            topics_status = {
                self.cam_imu_topic: self.cam_imu_topic in bag_info.topics,
                self.statustext_topic: self.statustext_topic in bag_info.topics,
                self.odom_topic: self.odom_topic in bag_info.topics
            }
            
            print(f"\n📋 Статус топиков:")
            for topic, exists in topics_status.items():
                status = "✅ НАЙДЕН" if exists else "❌ НЕ НАЙДЕН"
                print(f"  {topic}: {status}")
            
            if not all(topics_status.values()):
                raise ValueError("Не все необходимые топики найдены в bag файле!")
            
            # Извлечь данные
            print(f"\n📖 Чтение сообщений...")
            
            cam_count = 0
            photo_count = 0
            odom_count = 0
            
            for msg_tuple in bag.read_messages(topics=[
                self.cam_imu_topic,
                self.statustext_topic,
                self.odom_topic
            ]):
                topic = msg_tuple.topic
                msg = msg_tuple.message
                t = msg_tuple.timestamp
                
                if topic == self.cam_imu_topic:
                    # Извлечь метку времени камеры
                    self.camera_frames.append({
                        'bag_timestamp': t.to_sec(),
                        'frame_timestamp': msg.frame_stamp.to_sec(),
                        'seq_id': msg.frame_seq_id
                    })
                    cam_count += 1
                
                elif topic == self.statustext_topic:
                    # Извлечь имя файла (только сообщения с [PHOTO]:)
                    text = msg.text
                    if '[PHOTO]:' in text:
                        # Парсинг: [PHOTO]: image_20250919_175100_691924_seq1000.jpg
                        filename = text.split('[PHOTO]:')[1].strip()
                        self.photo_names[t.to_sec()] = filename
                        photo_count += 1
                
                elif topic == self.odom_topic:
                    # Извлечь позицию и ориентацию
                    pos = msg.pose.pose.position
                    orient = msg.pose.pose.orientation
                    
                    self.odometry_data.append({
                        'timestamp': t.to_sec(),
                        'x': pos.x,
                        'y': pos.y,
                        'z': pos.z,
                        'qx': orient.x,
                        'qy': orient.y,
                        'qz': orient.z,
                        'qw': orient.w
                    })
                    odom_count += 1
            
            print(f"\n✅ Извлечено данных:")
            print(f"   📸 Меток камеры: {cam_count}")
            print(f"   📝 Имён файлов: {photo_count}")
            print(f"   🎯 Позиций одометрии: {odom_count}")
    
    def match_frames_with_filenames(self, max_time_diff=1.0):
        """
        Сопоставить метки времени камеры с именами файлов.
        
        Parameters:
            max_time_diff: Максимальная разница во времени (секунды)
        """
        print("\n" + "=" * 80)
        print("🔗 СОПОСТАВЛЕНИЕ КАДРОВ С ИМЕНАМИ ФАЙЛОВ")
        print("=" * 80)
        
        matched = 0
        unmatched = 0
        
        for frame in self.camera_frames:
            cam_time = frame['bag_timestamp']
            
            # Найти ближайшее имя файла
            best_match = None
            min_diff = float('inf')
            
            for photo_time, filename in self.photo_names.items():
                time_diff = abs(cam_time - photo_time)
                
                if time_diff < min_diff:
                    min_diff = time_diff
                    best_match = (photo_time, filename)
            
            if best_match and min_diff < max_time_diff:
                frame['filename'] = best_match[1]
                frame['filename_time_diff'] = min_diff
                matched += 1
            else:
                frame['filename'] = None
                frame['filename_time_diff'] = None
                unmatched += 1
        
        print(f"\n📊 Результаты сопоставления:")
        print(f"   ✅ Сопоставлено: {matched}")
        print(f"   ⚠️  Не сопоставлено: {unmatched}")
        
        if matched > 0:
            time_diffs = [f['filename_time_diff'] for f in self.camera_frames if f['filename'] is not None]
            avg_diff = np.mean(time_diffs) * 1000  # в миллисекунды
            max_diff = np.max(time_diffs) * 1000
            
            print(f"   📈 Средняя разница времени: {avg_diff:.2f} мс")
            print(f"   📈 Максимальная разница: {max_diff:.2f} мс")
    
    def interpolate_positions(self):
        """
        Интерполировать позиции для каждого кадра на основе одометрии.
        """
        print("\n" + "=" * 80)
        print("🎯 ИНТЕРПОЛЯЦИЯ ПОЗИЦИЙ")
        print("=" * 80)
        
        if len(self.odometry_data) < 2:
            raise ValueError("Недостаточно данных одометрии для интерполяции!")
        
        # Подготовить данные одометрии для интерполяции
        odom_times = np.array([d['timestamp'] for d in self.odometry_data])
        odom_x = np.array([d['x'] for d in self.odometry_data])
        odom_y = np.array([d['y'] for d in self.odometry_data])
        odom_z = np.array([d['z'] for d in self.odometry_data])
        odom_qx = np.array([d['qx'] for d in self.odometry_data])
        odom_qy = np.array([d['qy'] for d in self.odometry_data])
        odom_qz = np.array([d['qz'] for d in self.odometry_data])
        odom_qw = np.array([d['qw'] for d in self.odometry_data])
        
        # Создать интерполяторы
        interp_x = interp1d(odom_times, odom_x, kind='linear', bounds_error=False, fill_value='extrapolate')
        interp_y = interp1d(odom_times, odom_y, kind='linear', bounds_error=False, fill_value='extrapolate')
        interp_z = interp1d(odom_times, odom_z, kind='linear', bounds_error=False, fill_value='extrapolate')
        interp_qx = interp1d(odom_times, odom_qx, kind='linear', bounds_error=False, fill_value='extrapolate')
        interp_qy = interp1d(odom_times, odom_qy, kind='linear', bounds_error=False, fill_value='extrapolate')
        interp_qz = interp1d(odom_times, odom_qz, kind='linear', bounds_error=False, fill_value='extrapolate')
        interp_qw = interp1d(odom_times, odom_qw, kind='linear', bounds_error=False, fill_value='extrapolate')
        
        # Интерполировать позиции для каждого кадра
        interpolated = 0
        
        for frame in self.camera_frames:
            if frame['filename'] is None:
                continue  # Пропустить кадры без имени файла
            
            # Использовать frame_timestamp для интерполяции
            frame_time = frame['frame_timestamp']
            
            try:
                # Интерполировать позицию
                x = float(interp_x(frame_time))
                y = float(interp_y(frame_time))
                z = float(interp_z(frame_time))
                qx = float(interp_qx(frame_time))
                qy = float(interp_qy(frame_time))
                qz = float(interp_qz(frame_time))
                qw = float(interp_qw(frame_time))
                
                # Сохранить результат
                self.camera_positions.append({
                    'timestamp': frame_time,
                    'seq_id': frame['seq_id'],
                    'filename': frame['filename'],
                    'x': x,
                    'y': y,
                    'z': z,
                    'qx': qx,
                    'qy': qy,
                    'qz': qz,
                    'qw': qw
                })
                
                interpolated += 1
                
            except Exception as e:
                print(f"   ⚠️  Ошибка интерполяции для кадра {frame['seq_id']}: {e}")
        
        print(f"\n✅ Интерполировано позиций: {interpolated}")
        
        if interpolated == 0:
            raise ValueError("Не удалось интерполировать ни одной позиции!")
    
    def save_to_csv(self, output_file):
        """
        Сохранить результаты в CSV файл.
        
        Parameters:
            output_file: Путь к выходному файлу
        """
        print(f"\n💾 Сохранение в CSV: {output_file}")
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Заголовок
            writer.writerow([
                'timestamp', 'seq_id', 'filename',
                'x', 'y', 'z',
                'qx', 'qy', 'qz', 'qw'
            ])
            
            # Данные
            for pos in self.camera_positions:
                writer.writerow([
                    pos['timestamp'],
                    pos['seq_id'],
                    pos['filename'],
                    pos['x'],
                    pos['y'],
                    pos['z'],
                    pos['qx'],
                    pos['qy'],
                    pos['qz'],
                    pos['qw']
                ])
        
        print(f"   ✅ Сохранено {len(self.camera_positions)} позиций")
    
    def save_to_json(self, output_file):
        """
        Сохранить результаты в JSON файл.
        
        Parameters:
            output_file: Путь к выходному файлу
        """
        print(f"\n💾 Сохранение в JSON: {output_file}")
        
        data = {
            'metadata': {
                'bag_file': self.bag_file,
                'export_time': datetime.now().isoformat(),
                'total_frames': len(self.camera_positions)
            },
            'frames': self.camera_positions
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Сохранено {len(self.camera_positions)} позиций")
    
    def save_to_agisoft_txt(self, output_file):
        """
        Сохранить в формате, совместимом с Agisoft Metashape.
        Формат: filename x y z qx qy qz qw
        
        Parameters:
            output_file: Путь к выходному файлу
        """
        print(f"\n💾 Сохранение в Agisoft TXT: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Заголовок (опционально)
            f.write("# Camera positions from ROS bag\n")
            f.write("# Format: filename x y z qx qy qz qw\n")
            f.write("#\n")
            
            # Данные
            for pos in self.camera_positions:
                f.write(f"{pos['filename']} "
                       f"{pos['x']:.6f} {pos['y']:.6f} {pos['z']:.6f} "
                       f"{pos['qx']:.6f} {pos['qy']:.6f} {pos['qz']:.6f} {pos['qw']:.6f}\n")
        
        print(f"   ✅ Сохранено {len(self.camera_positions)} позиций")
    
    def process(self, output_formats=['csv', 'json'], output_dir=None):
        """
        Полный процесс извлечения и сохранения данных.
        
        Parameters:
            output_formats: Список форматов ['csv', 'json', 'agisoft']
            output_dir: Директория для сохранения (по умолчанию - рядом с bag файлом)
        """
        print("=" * 80)
        print("🚀 НАЧАЛО ИЗВЛЕЧЕНИЯ ПОЗИЦИЙ КАМЕРЫ")
        print("=" * 80)
        
        # 1. Извлечь данные
        self.extract_data()
        
        # 2. Сопоставить кадры с именами файлов
        self.match_frames_with_filenames()
        
        # 3. Интерполировать позиции
        self.interpolate_positions()
        
        # 4. Сохранить результаты
        if output_dir is None:
            output_dir = os.path.dirname(self.bag_file)
        
        base_name = os.path.splitext(os.path.basename(self.bag_file))[0]
        
        print("\n" + "=" * 80)
        print("💾 СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")
        print("=" * 80)
        
        for fmt in output_formats:
            if fmt == 'csv':
                output_file = os.path.join(output_dir, f"{base_name}_camera_positions.csv")
                self.save_to_csv(output_file)
            
            elif fmt == 'json':
                output_file = os.path.join(output_dir, f"{base_name}_camera_positions.json")
                self.save_to_json(output_file)
            
            elif fmt == 'agisoft':
                output_file = os.path.join(output_dir, f"{base_name}_camera_positions_agisoft.txt")
                self.save_to_agisoft_txt(output_file)
        
        print("\n" + "=" * 80)
        print("✅ ИЗВЛЕЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("=" * 80)
        
        return self.camera_positions


def main():
    """
    Главная функция.
    """
    print("🎬 ИЗВЛЕЧЕНИЕ ПОЗИЦИЙ КАМЕРЫ ИЗ ROS BAG")
    print("=" * 80)
    
    # Получить путь к bag файлу
    bag_file = input("\n📁 Введите путь к ROS bag файлу: ").strip()
    bag_file = bag_file.strip('"').strip("'")
    
    if not os.path.exists(bag_file):
        print(f"❌ Файл не найден: {bag_file}")
        return
    
    # Выбрать форматы вывода
    print("\n📝 Выберите форматы вывода:")
    print("   1 - CSV (универсальный)")
    print("   2 - JSON (структурированный)")
    print("   3 - Agisoft TXT (для фотограмметрии)")
    print("   4 - Все форматы")
    
    choice = input("\nВыбор (Enter для CSV): ").strip()
    
    format_map = {
        '1': ['csv'],
        '2': ['json'],
        '3': ['agisoft'],
        '4': ['csv', 'json', 'agisoft'],
        '': ['csv']
    }
    
    output_formats = format_map.get(choice, ['csv'])
    
    # Директория вывода
    output_dir = input(f"\n📁 Директория для сохранения (Enter для '{os.path.dirname(bag_file)}'): ").strip()
    if not output_dir:
        output_dir = os.path.dirname(bag_file)
    
    try:
        # Создать экстрактор и обработать
        extractor = CameraPositionExtractor(bag_file)
        extractor.process(output_formats=output_formats, output_dir=output_dir)
        
        print(f"\n🎉 Готово! Проверьте файлы в: {output_dir}")
        
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
