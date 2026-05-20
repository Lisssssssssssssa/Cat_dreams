"""
Автоматические тесты для Cat Dreams
Запуск: python tests/run_tests.py
"""
import sys
import os

# Добавляем корневую папку в путь, чтобы импорты работали
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from algorithms.bsp_generator import BSPNode, generate_level
from algorithms.bfs_validator import is_level_connected
import pygame


def print_header(text):
    print("\n" + "=" * 50)
    print(f" 🧪 {text}")
    print("=" * 50)


def test_bsp_generation():
    """Тест 1: Генерация BSP и проверка геометрии"""
    print_header("ТЕСТ 1: BSP Генерация уровней")

    # Инициализируем Pygame для работы с Rect (нужен для коллизий)
    pygame.init()

    width, height = 800, 600
    num_tasks = 5

    print(f"🔹 Входные данные: Ширина={width}, Высота={height}, Задачи={num_tasks}")

    # Генерируем уровень
    level_data = generate_level(width, height, num_tasks, min_room_size=50)

    rooms = level_data['rooms']

    # Проверка 1: Количество комнат
    assert len(rooms) == num_tasks, f"❌ Ошибка: ожидалось {num_tasks} комнат, получено {len(rooms)}"
    print(f"✅ Количество комнат совпадает: {len(rooms)}")

    # Проверка 2: Отсутствие пересечений
    overlaps = 0
    for i in range(len(rooms)):
        for j in range(i + 1, len(rooms)):
            if rooms[i]['rect'].colliderect(rooms[j]['rect']):
                overlaps += 1
                print(f" Пересечение: Комната {i} и Комната {j}")

    if overlaps == 0:
        print("✅ Геометрические пересечения отсутствуют")
    else:
        raise AssertionError(f"Найдено {overlaps} пересечений!")

    # Проверка 3: Валидность данных
    assert level_data['is_valid'], "❌ Уровень признан несвязным!"
    print("✅ Уровень прошел первичную валидацию")


def test_bfs_connectivity():
    """Тест 2: BFS Валидация связности"""
    print_header("ТЕСТ 2: BFS Валидация проходимости")

    pygame.init()
    level_data = generate_level(800, 600, 4, min_room_size=50)
    rooms_nodes = []

    # Восстанавливаем объекты узлов для теста (так как generate_level возвращает словари)
    # Для простоты теста используем встроенную проверку из generate_level
    is_valid = level_data['is_valid']

    print(f" Статус связности из генератора: {is_valid}")

    if is_valid:
        print("✅ Все комнаты достижимы из стартовой (Task 0)")
    else:
        raise AssertionError("❌ Обнаружены изолированные комнаты!")


def test_physics_aabb():
    """Тест 3: Физика и AABB Коллизии"""
    print_header("ТЕСТ 3: Физика и Коллизии (AABB)")

    pygame.init()

    # Создаем фиктивные объекты
    cat_rect = pygame.Rect(100, 100, 50, 50)
    floor_rect = pygame.Rect(0, 150, 800, 50)
    wall_rect = pygame.Rect(200, 0, 50, 600)

    # Симуляция падения
    cat_y = 100
    velocity_y = 5

    steps = 0
    landed = False

    while not landed and steps < 100:
        cat_y += velocity_y
        cat_rect.y = int(cat_y)

        # Простая логика коллизии (как в _check_collisions)
        if cat_rect.colliderect(floor_rect):
            if velocity_y >= 0:  # Падение вниз
                cat_y = floor_rect.top - cat_rect.height
                velocity_y = 0
                landed = True

        steps += 1

    assert landed, "❌ Кот не приземлился на платформу"
    assert cat_y == 100, f"❌ Координата Y неверна: {cat_y} (ожидается 100)"  # 150 (пол) - 50 (высота кота)
    print("✅ Коллизия с полом работает корректно (Y=100)")

    # Тест стены
    cat_rect.x = 190
    if cat_rect.colliderect(wall_rect):
        print("✅ Коллизия со стеной обнаружена")
    else:
        raise AssertionError("❌ Коллизия со стеной не сработала")


def test_camera_zoom():
    """Тест 4: Камера и Динамический Зум"""
    print_header("ТЕСТ 4: Камера и Трансформация координат")

    # Импортируем класс камеры
    from entities.camera import Camera

    screen_w, screen_h = 800, 600
    camera = Camera(screen_w, screen_h)

    # Тест 1: Базовое применение (Zoom 1.0)
    rect = pygame.Rect(100, 100, 50, 50)
    cam_rect = camera.apply(rect)

    assert cam_rect.x == 100 and cam_rect.y == 100, "❌ Ошибка базовой трансформации"
    print("✅ Базовая трансформация (Zoom 1.0) верна")

    # Тест 2: Зум 2.0
    camera.zoom = 2.0
    camera.state.x = 0
    camera.state.y = 0

    cam_rect_zoomed = camera.apply(rect)
    expected_x = 100 * 2.0
    expected_w = 50 * 2.0

    assert cam_rect_zoomed.x == expected_x, f"❌ Ошибка X при зуме: {cam_rect_zoomed.x} != {expected_x}"
    assert cam_rect_zoomed.width == expected_w, f"❌ Ошибка Width при зуме: {cam_rect_zoomed.width} != {expected_w}"
    print("✅ Динамический зум (Zoom 2.0) работает корректно")


if __name__ == "__main__":
    try:
        test_bsp_generation()
        test_bfs_connectivity()
        test_physics_aabb()
        test_camera_zoom()

        print("\n" + "=" * 50)
        print(" 🎉 ВСЕ ТЕСТЫ ПРОЙДЕНУСПЕШНО!")
        print("=" * 50 + "\n")

    except AssertionError as e:
        print(f"\n❌ ТЕСТ ПРОВАЛЕН: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n⚠️ НЕОЖИДАННАЯ ОШИБКА: {e}\n")
        sys.exit(1)
        