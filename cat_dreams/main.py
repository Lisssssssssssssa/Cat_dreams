import pygame
import os
import config as cfg
from entities.cat import Cat
from entities.zoom import Camera
from algorithms.bsp_generation import generate_level


def load_backgrounds():
    """
    Загружает фоны для комнат и коридоров из папки assets/backgrounds/
    Возвращает словарь с поверхностями Pygame или None, если файл не найден.
    """
    backgrounds = {}
    bg_dir = os.path.join('assets', 'backgrounds')

    # 1. Загрузка фона комнат
    room_file = os.path.join(bg_dir, 'rooms.jpg')
    if os.path.exists(room_file):
        try:
            backgrounds['room'] = pygame.image.load(room_file).convert()
            print(f"✅ Фон комнат загружен: {room_file}")
        except Exception as e:
            print(f"❌ Ошибка загрузки rooms.jpg: {e}")
            backgrounds['room'] = None
    else:
        print(f"⚠️ Файл не найден: {room_file}")
        backgrounds['room'] = None

    # 2. Загрузка фона коридоров/стен
    wall_file = os.path.join(bg_dir, 'walls.jpg')
    if os.path.exists(wall_file):
        try:
            backgrounds['wall'] = pygame.image.load(wall_file).convert()
            print(f"✅ Фон коридоров загружен: {wall_file}")
        except Exception as e:
            print(f"❌ Ошибка загрузки walls.jpg: {e}")
            backgrounds['wall'] = None
    else:
        print(f"️ Файл не найден: {wall_file}")
        backgrounds['wall'] = None

    return backgrounds


def main():
    pygame.init()

    # Полноэкранный режим
    screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Cat Dreams - Level Editor 💤")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)

    # === ЗАГРУЗКА ФОНОВ ===
    backgrounds = load_backgrounds()

    room_bg = backgrounds.get('room')
    wall_bg = backgrounds.get('wall')

    # Размеры тайлов для замощения (по умолчанию 64x64, если картинки нет)
    r_w, r_h = (64, 64)
    w_w, w_h = (64, 64)

    if room_bg:
        r_w, r_h = room_bg.get_size()
    if wall_bg:
        w_w, w_h = wall_bg.get_size()

    # Генерация уровня
    print("🏗️ Генерация уровня...")
    level_data = generate_level(
        width=cfg.SCREEN_WIDTH,
        height=cfg.SCREEN_HEIGHT,
        num_tasks=5,
        min_room_size=200
    )

    if not level_data['is_valid']:
        print("❌ Ошибка: Уровень несвязный!")
        return

    print(f"✅ Уровень сгенерирован! Комнат: {len(level_data['rooms'])}")

    # Камера
    camera = Camera(cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)

    # Режимы: 'overview' / 'edit_room'
    game_mode = 'overview'
    selected_room = None

    # Кот (изначально в первой комнате)
    start_room = level_data['rooms'][0]['rect']
    cat = Cat(start_room.x + 50, start_room.y + 20)

    # Платформы (комнаты + коридоры)
    platforms = []
    for room in level_data['rooms']:
        platforms.append(room['rect'])
    platforms.extend(level_data['corridors'])

    running = True
    while running:
        dt = clock.tick(cfg.FPS)

        # === ОБРАБОТКА СОБЫТИЙ ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_BACKSPACE:
                    # Вернуться к общему виду
                    if game_mode == 'edit_room':
                        game_mode = 'overview'
                        camera.reset_zoom()
                        selected_room = None
                        # Возвращаем кота в первую комнату
                        cat.x = start_room.x + 50
                        cat.y = start_room.y + 20

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    if game_mode == 'overview':
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        world_x = (mouse_x / camera.zoom) + camera.state.x
                        world_y = (mouse_y / camera.zoom) + camera.state.y

                        for room in level_data['rooms']:
                            if room['rect'].collidepoint(world_x, world_y):
                                game_mode = 'edit_room'
                                selected_room = room

                                # === ДИНАМИЧЕСКИЙ ЗУМ ===
                                room_w = room['rect'].width
                                room_h = room['rect'].height
                                zoom_x = cfg.SCREEN_WIDTH / room_w
                                zoom_y = cfg.SCREEN_HEIGHT / room_h
                                base_zoom = min(zoom_x, zoom_y)
                                PADDING_FACTOR = 0.85
                                target_zoom = base_zoom * PADDING_FACTOR
                                target_zoom = max(0.4, min(target_zoom, 5.0))

                                camera.zoom = target_zoom
                                camera.target_zoom = target_zoom
                                camera.state.x = room['rect'].centerx - (cfg.SCREEN_WIDTH / 2) / target_zoom
                                camera.state.y = room['rect'].centery - (cfg.SCREEN_HEIGHT / 2) / target_zoom

                                # Спавним кота ВНУТРИ комнаты
                                cat.x = room['rect'].centerx - (cat.width // 2)
                                cat.y = room['rect'].y + 50
                                cat.velocity_x = 0
                                cat.velocity_y = 0
                                cat.on_ground = False
                                break

        # === ОБНОВЛЕНИЕ ===
        keys = pygame.key.get_pressed()

        if game_mode == 'overview':
            camera.update()
            cat.update(keys, platforms)
        else:
            if selected_room:
                cat.update(keys, [selected_room['rect']])

        # === ОТРИСОВКА ===
        screen.fill(cfg.BLACK)

        if game_mode == 'overview':
            # --- СЛОЙ 1: ФОН СТЕН (заполняет весь экран как база) ---
            if wall_bg:
                # Вычисляем смещение для бесконечного замощения относительно камеры
                offset_x = int(-camera.state.x % w_w)
                offset_y = int(-camera.state.y % w_h)

                # Рисуем сетку тайлов, покрывающую экран с запасом
                for y in range(-w_h, cfg.SCREEN_HEIGHT + w_h, w_h):
                    for x in range(-w_w, cfg.SCREEN_WIDTH + w_w, w_w):
                        screen.blit(wall_bg, (x + offset_x, y + offset_y))

            # --- СЛОЙ 2: ФОН КОМНАТ (поверх стен) ---
            if room_bg:
                for room in level_data['rooms']:
                    cam_rect = camera.apply(room['rect'])
                    # Замощаем фон только внутри прямоугольника комнаты
                    for y in range(cam_rect.top, cam_rect.bottom, r_h):
                        for x in range(cam_rect.left, cam_rect.right, r_w):
                            tile_rect = pygame.Rect(x, y, r_w, r_h)
                            if tile_rect.colliderect(cam_rect):
                                screen.blit(room_bg, (x, y))

            # --- СЛОЙ 3: КОРИДОРЫ (как платформы, можно сделать полупрозрачными или цветными) ---
            for corridor in level_data['corridors']:
                cam_rect = camera.apply(corridor)
                # Рисуем коридоры серым цветом поверх фона стен, чтобы выделить путь
                pygame.draw.rect(screen, (50, 50, 50), cam_rect)

                # --- СЛОЙ 4: РАМКИ И UI ---
            for room in level_data['rooms']:
                cam_rect = camera.apply(room['rect'])
                pygame.draw.rect(screen, cfg.BLUE, cam_rect, 2)

                text_pos = camera.apply_pos((room['rect'].x + 10, room['rect'].y + 10))
                text = font.render(f"Task {room['task_id']} (клик)", True, cfg.WHITE)
                screen.blit(text, text_pos)

            # Кот
            cat.draw_with_camera(screen, camera)

            # Подсказка
            hint = font.render("ESC - выход | Клик по комнате - редактировать | BACKSPACE - назад", True, cfg.WHITE)
            screen.blit(hint, (10, cfg.SCREEN_HEIGHT - 30))

        else:
            # --- РЕЖИМ РЕДАКТИРОВАНИЯ КОМНАТЫ ---
            if selected_room:
                # Фон стен на заднем плане
                if wall_bg:
                    offset_x = int(-camera.state.x % w_w)
                    offset_y = int(-camera.state.y % w_h)
                    for y in range(-w_h, cfg.SCREEN_HEIGHT + w_h, w_h):
                        for x in range(-w_w, cfg.SCREEN_WIDTH + w_w, w_w):
                            screen.blit(wall_bg, (x + offset_x, y + offset_y))

                # Фон выбранной комнаты
                if room_bg:
                    cam_rect = camera.apply(selected_room['rect'])
                    for y in range(cam_rect.top, cam_rect.bottom, r_h):
                        for x in range(cam_rect.left, cam_rect.right, r_w):
                            tile_rect = pygame.Rect(x, y, r_w, r_h)
                            if tile_rect.colliderect(cam_rect):
                                screen.blit(room_bg, (x, y))

                # Рамка и UI
                cam_rect = camera.apply(selected_room['rect'])
                pygame.draw.rect(screen, cfg.BLUE, cam_rect, 3)

                text_pos = camera.apply_pos((selected_room['rect'].x + 10, selected_room['rect'].y + 10))
                text = font.render(f"Task {selected_room['task_id']} (BACKSPACE - назад)", True, cfg.WHITE)
                screen.blit(text, text_pos)

                # Кот
                cat.draw_with_camera(screen, camera)

                hint = font.render("WASD - движение | Пробел - прыжок | BACKSPACE - назад", True, cfg.WHITE)
                screen.blit(hint, (10, cfg.SCREEN_HEIGHT - 30))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()