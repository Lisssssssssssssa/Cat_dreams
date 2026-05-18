graph TD
    %% === CORE LOOP ===
    Main["main.py<br/>(Game Loop + States)<br/>States: MENU ←→ GAME ←→ EDITOR ←→ PAUSE ←→ CUTSCENE"]

    %% === MANAGERS & RENDER ===
    SceneMgr["SCENE MANAGER<br/>- current_scene<br/>- switch()<br/>- transitions"]
    Renderer["RENDERER<br/>- camera<br/>- particles<br/>- effects"]

    %% === ENTITIES LAYER ===
    Entities["ENTITIES<br/>Cat | Enemy | Platform<br/>- physics | ai | type<br/>- animations | path | rect<br/>- controls | state"]

    %% === COMPONENTS ===
    Anim["Animation<br/>- frames<br/>- fps<br/>- update()"]
    Camera["Camera System<br/>- zoom (0.4-5x)<br/>- state (rect)<br/>- apply()"]

    %% === ALGORITHMS ===
    Algos["ALGORITHMS<br/>BSPGenerator<br/>- split()<br/>- create_room()<br/>- build_corridors()"]
    BFS["BFSValidator<br/>- is_connected()"]

    %% === GLOBAL SYSTEMS ===
    Systems["SYSTEMS<br/>AudioManager<br/>SaveSystem<br/>InputHandler<br/>Pathfinder (A*)"]

    %% === CONNECTIONS ===
    Main --> SceneMgr
    Main --> Renderer
    SceneMgr --> Entities
    Entities --> Anim
    Entities --> Camera
    Anim --> Algos
    Algos --> BFS
    Systems -.-> Main : "глобальные сервисы"

    %% === STYLING ===
    classDef default fill:#ffffff,stroke:#333333,stroke-width:1.5px,rx:5px,ry:5px;
    classDef core fill:#e3f2fd,stroke:#1565c0,stroke-width:2px;
    classDef sys fill:#fff8e1,stroke:#f57f17,stroke-width:1.5px,stroke-dasharray: 5 5;
    class Main core;
    class Systems sys;