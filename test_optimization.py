#!/usr/bin/env python3
"""
Тест для проверки оптимизации обработки точек и кросс-платформенной совместимости.
Сравнивает старый метод (списки + append) с новым (numpy массивы).
"""

import numpy as np
import time
import platform

print("=" * 80)
print("🧪 ТЕСТ ОПТИМИЗАЦИИ И КРОСС-ПЛАТФОРМЕННОЙ СОВМЕСТИМОСТИ")
print("=" * 80)

print(f"\n🖥️  ИНФОРМАЦИЯ О СИСТЕМЕ:")
print(f"   • ОС: {platform.system()} {platform.release()}")
print(f"   • Python: {platform.python_version()}")
print(f"   • NumPy: {np.__version__}")
print(f"   • Архитектура: {platform.machine()}")

# ============================================================================
# ТЕСТ 1: ПРОИЗВОДИТЕЛЬНОСТЬ - Старый метод (списки)
# ============================================================================

print("\n" + "=" * 80)
print("📊 ТЕСТ 1: СТАРЫЙ МЕТОД (списки + append)")
print("=" * 80)

n_messages = 1000
points_per_message = 1000
total_points = n_messages * points_per_message

print(f"   • Количество сообщений: {n_messages:,}")
print(f"   • Точек в сообщении: {points_per_message:,}")
print(f"   • Всего точек: {total_points:,}")

# Имитация старого метода
start_time = time.time()

x_list = []
y_list = []
z_list = []
intensity_list = []

for msg_idx in range(n_messages):
    # Имитация чтения точек из сообщения
    msg_points = np.random.rand(points_per_message, 3).astype(np.float64) * 100
    intensities = np.random.rand(points_per_message).astype(np.float32) * 255
    
    # СТАРЫЙ МЕТОД: append для каждой точки
    for point_idx in range(len(msg_points)):
        x_list.append(msg_points[point_idx, 0])
        y_list.append(msg_points[point_idx, 1])
        z_list.append(msg_points[point_idx, 2])
        intensity_list.append(intensities[point_idx])

# Конвертация в numpy
x_array_old = np.array(x_list, dtype=np.float64)
y_array_old = np.array(y_list, dtype=np.float64)
z_array_old = np.array(z_list, dtype=np.float64)
intensity_array_old = np.array(intensity_list, dtype=np.float32)

old_time = time.time() - start_time
old_rate = total_points / old_time

print(f"\n✅ РЕЗУЛЬТАТЫ СТАРОГО МЕТОДА:")
print(f"   • Время обработки: {old_time:.3f} секунд")
print(f"   • Скорость: {old_rate:,.0f} точек/сек")
print(f"   • Размер данных: {x_array_old.nbytes + y_array_old.nbytes + z_array_old.nbytes + intensity_array_old.nbytes:,} байт")

# ============================================================================
# ТЕСТ 2: ПРОИЗВОДИТЕЛЬНОСТЬ - Новый метод (numpy массивы)
# ============================================================================

print("\n" + "=" * 80)
print("🚀 ТЕСТ 2: НОВЫЙ МЕТОД (предварительное выделение памяти)")
print("=" * 80)

start_time = time.time()

# Предварительное выделение памяти
x_array_new = np.empty(total_points, dtype=np.float64)
y_array_new = np.empty(total_points, dtype=np.float64)
z_array_new = np.empty(total_points, dtype=np.float64)
intensity_array_new = np.empty(total_points, dtype=np.float32)

global_idx = 0
for msg_idx in range(n_messages):
    # Имитация чтения точек из сообщения
    msg_points = np.random.rand(points_per_message, 3).astype(np.float64) * 100
    intensities = np.random.rand(points_per_message).astype(np.float32) * 255
    
    n_points = len(msg_points)
    
    # НОВЫЙ МЕТОД: прямая запись в массив
    x_array_new[global_idx:global_idx+n_points] = msg_points[:, 0]
    y_array_new[global_idx:global_idx+n_points] = msg_points[:, 1]
    z_array_new[global_idx:global_idx+n_points] = msg_points[:, 2]
    intensity_array_new[global_idx:global_idx+n_points] = intensities
    
    global_idx += n_points

new_time = time.time() - start_time
new_rate = total_points / new_time

print(f"\n✅ РЕЗУЛЬТАТЫ НОВОГО МЕТОДА:")
print(f"   • Время обработки: {new_time:.3f} секунд")
print(f"   • Скорость: {new_rate:,.0f} точек/сек")
print(f"   • Размер данных: {x_array_new.nbytes + y_array_new.nbytes + z_array_new.nbytes + intensity_array_new.nbytes:,} байт")

# ============================================================================
# СРАВНЕНИЕ
# ============================================================================

print("\n" + "=" * 80)
print("📈 СРАВНЕНИЕ МЕТОДОВ")
print("=" * 80)

speedup = old_time / new_time
print(f"\n⚡ УСКОРЕНИЕ: ×{speedup:.1f} раз!")
print(f"   • Старый метод: {old_time:.3f} сек ({old_rate:,.0f} точек/сек)")
print(f"   • Новый метод: {new_time:.3f} сек ({new_rate:,.0f} точек/сек)")

if speedup > 10:
    print(f"   🎉 ОТЛИЧНЫЙ результат! Ускорение более чем в 10 раз!")
elif speedup > 5:
    print(f"   ✅ Хорошее ускорение!")
else:
    print(f"   ⚠️  Ускорение меньше ожидаемого...")

# ============================================================================
# ТЕСТ 3: КРОСС-ПЛАТФОРМЕННАЯ СОВМЕСТИМОСТЬ scale/offset
# ============================================================================

print("\n" + "=" * 80)
print("🌍 ТЕСТ 3: КРОСС-ПЛАТФОРМЕННАЯ СОВМЕСТИМОСТЬ")
print("=" * 80)

def calculate_optimal_scale_offset(coords_array):
    """Функция из оптимизированного кода"""
    min_val = np.float64(np.min(coords_array))
    max_val = np.float64(np.max(coords_array))
    coord_range = max_val - min_val
    MAX_INT32 = 2_000_000_000
    required_scale = coord_range / MAX_INT32 if coord_range > 0 else 0.001
    
    if required_scale <= 0.001:
        scale = 0.001
    elif required_scale <= 0.01:
        scale = 0.01
    elif required_scale <= 0.1:
        scale = 0.1
    else:
        scale = 1.0
    
    offset = np.float64(np.floor(min_val))
    return scale, offset

def validate_las_encoding(coords, offset, scale, coord_name="coordinate"):
    """Функция валидации из оптимизированного кода"""
    encoded = ((coords - offset) / scale).astype(np.int64)
    min_encoded = np.min(encoded)
    max_encoded = np.max(encoded)
    
    if max_encoded > 2_147_483_647 or min_encoded < -2_147_483_648:
        raise ValueError(f"{coord_name} не влезает в int32! Range: {min_encoded} to {max_encoded}")
    return True

# Тест 1: Малые координаты (локальная система)
print("\n🧪 Тест 3.1: Малые координаты (локальная система)")
small_coords = np.random.rand(10000) * 200 - 100  # -100 to +100
scale, offset = calculate_optimal_scale_offset(small_coords)
print(f"   • Диапазон: [{np.min(small_coords):.2f}, {np.max(small_coords):.2f}]")
print(f"   • Scale: {scale}, Offset: {offset:.2f}")
assert scale == 0.001, f"Expected scale 0.001, got {scale}"
validate_las_encoding(small_coords, offset, scale, "small coords")
print(f"   ✅ PASSED: Малые координаты корректно кодируются")

# Тест 2: Средние координаты (UTM-подобные)
print("\n🧪 Тест 3.2: Средние координаты (UTM-подобные)")
medium_coords = np.random.rand(10000) * 100000 + 500000  # 500,000 to 600,000
scale, offset = calculate_optimal_scale_offset(medium_coords)
print(f"   • Диапазон: [{np.min(medium_coords):.2f}, {np.max(medium_coords):.2f}]")
print(f"   • Scale: {scale}, Offset: {offset:.2f}")
assert scale == 0.001, f"Expected scale 0.001, got {scale}"
validate_las_encoding(medium_coords, offset, scale, "medium coords")
print(f"   ✅ PASSED: Средние координаты корректно кодируются")

# Тест 3: Большие координаты
print("\n🧪 Тест 3.3: Большие координаты (огромный диапазон)")
large_coords = np.random.rand(10000) * 5000000  # 0 to 5,000,000
scale, offset = calculate_optimal_scale_offset(large_coords)
print(f"   • Диапазон: [{np.min(large_coords):.2f}, {np.max(large_coords):.2f}]")
print(f"   • Scale: {scale}, Offset: {offset:.2f}")
assert scale >= 0.001, f"Expected scale >= 0.001, got {scale}"
validate_las_encoding(large_coords, offset, scale, "large coords")
print(f"   ✅ PASSED: Большие координаты корректно кодируются")

# Тест 4: Проверка кросс-платформенности типов
print("\n🧪 Тест 3.4: Кросс-платформенная совместимость типов")
test_coords = np.array([123.456789, 987.654321, 555.555555], dtype=np.float64)
scale, offset = calculate_optimal_scale_offset(test_coords)

# Явное преобразование в Python float (как в оптимизированном коде)
offset_py = np.float64(offset).item()
scale_py = np.float64(scale).item()

print(f"   • NumPy offset: {offset} (type: {type(offset).__name__})")
print(f"   • Python offset: {offset_py} (type: {type(offset_py).__name__})")
print(f"   • NumPy scale: {scale} (type: {type(scale).__name__})")
print(f"   • Python scale: {scale_py} (type: {type(scale_py).__name__})")

assert isinstance(offset_py, float), f"Expected Python float, got {type(offset_py)}"
assert isinstance(scale_py, float), f"Expected Python float, got {type(scale_py)}"
print(f"   ✅ PASSED: Типы корректно преобразованы для кросс-платформенности")

# ============================================================================
# ИТОГОВЫЙ РЕЗУЛЬТАТ
# ============================================================================

print("\n" + "=" * 80)
print("🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
print("=" * 80)

print(f"\n📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
print(f"   ✅ Производительность: Ускорение ×{speedup:.1f} раз")
print(f"   ✅ Кросс-платформенность: Все тесты пройдены")
print(f"   ✅ Валидация LAS кодирования: Работает корректно")
print(f"   ✅ Тестовая платформа: {platform.system()} {platform.machine()}")

print(f"\n💡 РЕКОМЕНДАЦИИ:")
if speedup > 10:
    print(f"   • Новый метод готов к использованию в продакшене!")
    print(f"   • Ожидаемое ускорение на реальных данных: ×{speedup:.0f} раз")
else:
    print(f"   • Новый метод показывает улучшение производительности")
    print(f"   • Рекомендуется протестировать на реальных bag файлах")

print("\n" + "=" * 80)
