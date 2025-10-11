#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый файл для дебага извлечения меток времени камеры из ROS bag
Топики:
  - /mavros/cam_imu_sync/cam_imu_stamp (тип mavros_msgs/CamIMUStamp) - время кадра
  - /mavros/statustext/send (тип mavros_msgs/StatusText) - имя файла
  - Топик одометрии для позиции (определяется автоматически)
"""

import rosbag
import os
from datetime import datetime
from collections import defaultdict
import json


def analyze_bag_topics(bag_file):
    """
    Анализ топиков в ROS bag файле.
    """
    print("=" * 80)
    print("📊 АНАЛИЗ ТОПИКОВ В BAG ФАЙЛЕ")
    print("=" * 80)
    
    topics_info = defaultdict(lambda: {"count": 0, "type": None, "first_time": None, "last_time": None})
    
    with rosbag.Bag(bag_file, 'r') as bag:
        # Получить информацию о топиках
        bag_info = bag.get_type_and_topic_info()
        
        print(f"\n📦 Файл: {os.path.basename(bag_file)}")
        print(f"🕐 Начало: {datetime.fromtimestamp(bag.get_start_time())}")
        print(f"🕑 Конец: {datetime.fromtimestamp(bag.get_end_time())}")
        print(f"⏱️  Длительность: {bag.get_end_time() - bag.get_start_time():.2f} сек")
        print(f"\n📋 Всего топиков: {len(bag_info.topics)}")
        print("-" * 80)
        
        # Показать все топики
        for topic, info in bag_info.topics.items():
            topics_info[topic]["count"] = info.message_count
            topics_info[topic]["type"] = info.msg_type
            topics_info[topic]["frequency"] = info.frequency
        
        # Вывести информацию о топиках
        print(f"\n{'Топик':<50} {'Тип':<35} {'Кол-во':<10}")
        print("-" * 95)
        
        # Сортировка по имени топика
        for topic in sorted(topics_info.keys()):
            info = topics_info[topic]
            print(f"{topic:<50} {info['type']:<35} {info['count']:<10}")
    
    return topics_info


def debug_camera_messages(bag_file, max_messages=50):
    """
    Отладочная функция для просмотра сообщений камеры.
    
    Parameters:
        bag_file: Путь к ROS bag файлу
        max_messages: Максимальное количество сообщений для отображения
    """
    print("\n" + "=" * 80)
    print("🔍 ОТЛАДКА СООБЩЕНИЙ КАМЕРЫ")
    print("=" * 80)
    
    # Топики для отслеживания
    cam_imu_topic = "/mavros/cam_imu_sync/cam_imu_stamp"
    statustext_topic = "/mavros/statustext/send"
    
    cam_messages = []
    status_messages = []
    
    with rosbag.Bag(bag_file, 'r') as bag:
        # Проверить наличие топиков
        bag_info = bag.get_type_and_topic_info()
        
        has_cam_imu = cam_imu_topic in bag_info.topics
        has_statustext = statustext_topic in bag_info.topics
        
        print(f"\n✓ Топик {cam_imu_topic}: {'НАЙДЕН' if has_cam_imu else 'НЕ НАЙДЕН'}")
        if has_cam_imu:
            print(f"  Тип: {bag_info.topics[cam_imu_topic].msg_type}")
            print(f"  Сообщений: {bag_info.topics[cam_imu_topic].message_count}")
        
        print(f"\n✓ Топик {statustext_topic}: {'НАЙДЕН' if has_statustext else 'НЕ НАЙДЕН'}")
        if has_statustext:
            print(f"  Тип: {bag_info.topics[statustext_topic].msg_type}")
            print(f"  Сообщений: {bag_info.topics[statustext_topic].message_count}")
        
        if not (has_cam_imu or has_statustext):
            print("\n⚠️  Ни один из нужных топиков не найден!")
            return
        
        # Считать сообщения
        print(f"\n📖 Чтение сообщений (макс. {max_messages} на топик)...")
        
        topics_to_read = []
        if has_cam_imu:
            topics_to_read.append(cam_imu_topic)
        if has_statustext:
            topics_to_read.append(statustext_topic)
        
        for msg_tuple in bag.read_messages(topics=topics_to_read):
            topic = msg_tuple.topic
            msg = msg_tuple.message
            t = msg_tuple.timestamp
            
            if topic == cam_imu_topic and len(cam_messages) < max_messages:
                cam_messages.append({
                    'timestamp': t.to_sec(),
                    'ros_time': t,
                    'message': msg
                })
            elif topic == statustext_topic and len(status_messages) < max_messages:
                status_messages.append({
                    'timestamp': t.to_sec(),
                    'ros_time': t,
                    'message': msg
                })
            
            # Прервать если собрали достаточно
            if len(cam_messages) >= max_messages and len(status_messages) >= max_messages:
                break
    
    # Вывести сообщения cam_imu_sync
    if cam_messages:
        print(f"\n" + "=" * 80)
        print(f"📸 CAM_IMU_SYNC СООБЩЕНИЯ (первые {len(cam_messages)}):")
        print("=" * 80)
        
        for i, msg_data in enumerate(cam_messages[:10], 1):  # Показать первые 10
            msg = msg_data['message']
            timestamp = msg_data['timestamp']
            
            print(f"\n[{i}] Время bag: {datetime.fromtimestamp(timestamp)}")
            print(f"    ROS timestamp: {timestamp}")
            
            # Попытаться прочитать поля сообщения
            try:
                print(f"    Тип сообщения: {type(msg).__name__}")
                print(f"    Поля: {[slot for slot in msg.__slots__]}")
                
                # Вывести все доступные поля
                for slot in msg.__slots__:
                    value = getattr(msg, slot, None)
                    if value is not None:
                        # Если это ROS Time, преобразовать в читаемый формат
                        if hasattr(value, 'to_sec'):
                            print(f"    {slot}: {value.to_sec()} ({datetime.fromtimestamp(value.to_sec())})")
                        else:
                            print(f"    {slot}: {value}")
            except Exception as e:
                print(f"    ⚠️  Ошибка чтения полей: {e}")
                print(f"    Сырое сообщение: {msg}")
    else:
        print("\n⚠️  Сообщений cam_imu_sync не найдено")
    
    # Вывести сообщения statustext
    if status_messages:
        print(f"\n" + "=" * 80)
        print(f"📝 STATUSTEXT СООБЩЕНИЯ (первые {len(status_messages)}):")
        print("=" * 80)
        
        for i, msg_data in enumerate(status_messages[:10], 1):  # Показать первые 10
            msg = msg_data['message']
            timestamp = msg_data['timestamp']
            
            print(f"\n[{i}] Время bag: {datetime.fromtimestamp(timestamp)}")
            print(f"    ROS timestamp: {timestamp}")
            
            # Попытаться прочитать поля сообщения
            try:
                print(f"    Тип сообщения: {type(msg).__name__}")
                print(f"    Поля: {[slot for slot in msg.__slots__]}")
                
                # Вывести все доступные поля
                for slot in msg.__slots__:
                    value = getattr(msg, slot, None)
                    if value is not None:
                        print(f"    {slot}: {value}")
            except Exception as e:
                print(f"    ⚠️  Ошибка чтения полей: {e}")
                print(f"    Сырое сообщение: {msg}")
    else:
        print("\n⚠️  Сообщений statustext не найдено")
    
    # Анализ временной корреляции
    if cam_messages and status_messages:
        print(f"\n" + "=" * 80)
        print("⏱️  АНАЛИЗ ВРЕМЕННОЙ КОРРЕЛЯЦИИ")
        print("=" * 80)
        
        # Найти ближайшие пары сообщений
        print("\n🔗 Поиск парных сообщений (cam_imu + statustext в пределах 1 сек):")
        
        matches = []
        for cam_msg in cam_messages[:20]:
            cam_time = cam_msg['timestamp']
            
            # Найти ближайшее statustext сообщение
            closest_status = None
            min_diff = float('inf')
            
            for status_msg in status_messages:
                status_time = status_msg['timestamp']
                time_diff = abs(cam_time - status_time)
                
                if time_diff < min_diff:
                    min_diff = time_diff
                    closest_status = status_msg
            
            if closest_status and min_diff < 1.0:  # В пределах 1 секунды
                matches.append({
                    'cam_msg': cam_msg,
                    'status_msg': closest_status,
                    'time_diff': min_diff
                })
        
        if matches:
            print(f"\n✅ Найдено {len(matches)} парных сообщений:")
            for i, match in enumerate(matches[:5], 1):
                print(f"\n  [{i}] Разница времени: {match['time_diff']*1000:.2f} мс")
                print(f"      CAM время: {datetime.fromtimestamp(match['cam_msg']['timestamp'])}")
                print(f"      STATUS время: {datetime.fromtimestamp(match['status_msg']['timestamp'])}")
                
                # Попытаться извлечь текст из statustext
                try:
                    status_msg = match['status_msg']['message']
                    if hasattr(status_msg, 'text'):
                        print(f"      Текст: {status_msg.text}")
                except:
                    pass
        else:
            print("\n⚠️  Парных сообщений не найдено (разница > 1 сек)")


def find_odometry_topics(bag_file):
    """
    Поиск топиков одометрии в bag файле.
    """
    print("\n" + "=" * 80)
    print("🎯 ПОИСК ТОПИКОВ ОДОМЕТРИИ")
    print("=" * 80)
    
    odometry_topics = []
    
    with rosbag.Bag(bag_file, 'r') as bag:
        bag_info = bag.get_type_and_topic_info()
        
        # Искать топики с типом Odometry
        for topic, info in bag_info.topics.items():
            if 'Odometry' in info.msg_type or 'odometry' in topic.lower():
                odometry_topics.append({
                    'topic': topic,
                    'type': info.msg_type,
                    'count': info.message_count,
                    'frequency': info.frequency
                })
        
        if odometry_topics:
            print(f"\n✅ Найдено топиков одометрии: {len(odometry_topics)}")
            print("-" * 80)
            print(f"{'Топик':<50} {'Тип':<30} {'Сообщений':<12} {'Частота':<10}")
            print("-" * 80)
            
            for odom in odometry_topics:
                freq_str = f"{odom['frequency']:.1f} Hz" if odom['frequency'] else "N/A"
                print(f"{odom['topic']:<50} {odom['type']:<30} {odom['count']:<12} {freq_str:<10}")
        else:
            print("\n⚠️  Топики одометрии не найдены")
    
    return odometry_topics


def main():
    """
    Главная функция для запуска отладки.
    """
    print("🎬 ОТЛАДКА ИЗВЛЕЧЕНИЯ МЕТОК ВРЕМЕНИ КАМЕРЫ")
    print("=" * 80)
    
    # Получить путь к bag файлу
    bag_file = input("\n📁 Введите путь к ROS bag файлу: ").strip()
    
    # Убрать кавычки если есть
    bag_file = bag_file.strip('"').strip("'")
    
    if not os.path.exists(bag_file):
        print(f"❌ Файл не найден: {bag_file}")
        return
    
    if not bag_file.endswith('.bag'):
        print(f"⚠️  Предупреждение: файл не имеет расширения .bag")
    
    try:
        # 1. Анализ всех топиков
        topics_info = analyze_bag_topics(bag_file)
        
        # 2. Поиск топиков одометрии
        odometry_topics = find_odometry_topics(bag_file)
        
        # 3. Отладка сообщений камеры
        max_msgs = input("\n📊 Сколько сообщений показать для отладки? (Enter для 50): ").strip()
        max_msgs = int(max_msgs) if max_msgs else 50
        
        debug_camera_messages(bag_file, max_messages=max_msgs)
        
        # 4. Сохранить результаты в JSON
        save_results = input("\n💾 Сохранить результаты в JSON? (y/n, Enter=y): ").strip().lower()
        if save_results in ['', 'y', 'yes', 'да', 'д']:
            output_file = os.path.join(
                os.path.dirname(bag_file),
                f"camera_debug_{os.path.basename(bag_file).replace('.bag', '')}.json"
            )
            
            results = {
                'bag_file': bag_file,
                'analysis_time': datetime.now().isoformat(),
                'topics': {topic: {'type': info['type'], 'count': info['count']} 
                          for topic, info in topics_info.items()},
                'odometry_topics': odometry_topics
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ Результаты сохранены: {output_file}")
        
        print("\n" + "=" * 80)
        print("✅ ОТЛАДКА ЗАВЕРШЕНА")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
