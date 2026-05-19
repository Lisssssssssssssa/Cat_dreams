## 🏗️ Архитектура проекта Cat Dreams
### Диаграмма классов

```mermaid
classDiagram
    class Config {
        <<configuration>>
        +int SCREEN_WIDTH
        +int SCREEN_HEIGHT
        +int FPS
        +float GRAVITY
        +float JUMP_POWER
        +float SPEED
        +str SPRITES_PATH
    }

    class Cat {
        -float x
        -float y
        -float velocity_x
        -float velocity_y
        -bool on_ground
        -bool facing_right
        -int width
        -int height
        -Rect rect
        -dict animations
        -str current_animation
        +__init__(x, y)
        +update(keys, platforms)
        +jump()
        +draw(screen)
        -_check_collisions(platforms)
    }

    class Animation {
        -list frames
        -int fps
        -bool loop
        -int current_frame
        -int frame_timer
        -int start_frame
        +__init__(filename, frame_w, frame_h, num_frames, fps, loop, start_frame)
        +update()
        +get_frame() Image
    }

    class Camera {
        -Rect state
        -float zoom
        -float target_zoom
        +__init__(width, height)
        +apply(entity_rect) Rect
        +apply_pos(pos) Tuple
        +update(target_rect)
        +zoom_in()
        +zoom_out()
        +reset_zoom()
    }

    class BSPGenerator {
        -BSPNode root
        -int num_tasks
        -int min_size
        +__init__(width, height, num_tasks, min_size)
        +generate_level() Dict
        -split_until_tasks() List
        -build_connectivity_graph() List
    }

    class BFSValidator {
        +is_level_connected(rooms) bool
    }

    class MainGameLoop {
        -Cat 
        -Camera 
        -Dict level_data
        +main()
        -handle_events()
        -update(dt)
        -render()
        -switch_state(mode)
    }

    %% === СВЯЗИ И ЗАВИСИМОСТИ ===
    MainGameLoop --> Camera : управляет видом
    MainGameLoop --> Cat : контролирует игрока
    MainGameLoop --> BSPGenerator : запускает генерацию
    MainGameLoop --> Config : читает настройки
    Cat --> Animation : содержит (композиция)
    Cat --> Config : использует физику
    Animation --> Config : использует пути к ассетам
    Camera --> Config : использует размеры экрана
    BSPGenerator --> BFSValidator : валидирует связность
    BFSValidator ..> BSPGenerator : возвращает результат

    %% === СТИЛИЗАЦИЯ (добавлен color:#000000 для чёрного текста) ===
    classDef default fill:#ffffff,stroke:#333333,stroke-width:1.5px,rx:5px,ry:5px,color:#000000;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#000000;
    classDef algo fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1.5px,color:#000000;
    classDef sys fill:#fff8e1,stroke:#f57f17,stroke-width:1.5px,color:#000000;
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px,stroke-dasharray: 5 5,color:#000000;

    class MainGameLoop core
    class BSPGenerator algo
    class BFSValidator algo
    class Camera sys
    class Config data

    class MainGameLoop core
    class BSPGenerator algo
    class BFSValidator algo

    class Camera sys
    class Config data
```