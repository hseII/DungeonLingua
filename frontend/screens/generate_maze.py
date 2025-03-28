import random

def generate_base_maze(min_rooms, max_rooms):
    """Генерирует основное дерево с гарантированной конечной комнатой"""
    num_rooms = random.randint(min_rooms, max_rooms)
    maze = {"room1": []}
    rooms = ["room1"]

    while len(rooms) < num_rooms:
        if len(rooms) == num_rooms - 1:
            parent = random.choice([r for r in rooms if r != "room1"] if len(rooms) > 1 else rooms)
            new_room = f"room{len(rooms) + 1}"
            maze[parent].append(new_room)
            maze[new_room] = [parent]
            rooms.append(new_room)
            break

        parent = random.choice([r for r in rooms if r != "room1"] if len(rooms) > 1 else rooms)
        new_room = f"room{len(rooms) + 1}"
        maze[parent].append(new_room)
        maze[new_room] = [parent]
        rooms.append(new_room)

    return maze, len(rooms), rooms[-1]


def add_traps(maze, last_room_id, min_traps, max_traps, final_room_id):
    """Добавляет ловушки, исключая финальную комнату"""
    num_traps = random.randint(min_traps, max_traps)

    eligible_rooms = [
        room for room in maze.keys()
        if (room.startswith("room")
            and room != "room1"
            and room != final_room_id
            and len(maze[room]) == 2)
    ]

    if not eligible_rooms:
        eligible_rooms = [
            room for room in maze.keys()
            if (room.startswith("room")
                and room != "room1"
                and room != final_room_id
                and len(maze[room]) == 1)
        ]

    if not eligible_rooms:
        return maze

    traps_added = 0
    while traps_added < num_traps and eligible_rooms:
        parent = random.choice(eligible_rooms)
        trap_name = f"room{last_room_id + traps_added + 1}"
        maze[parent].append(trap_name)
        maze[trap_name] = []
        traps_added += 1

        if random.random() > 0.5:
            eligible_rooms.remove(parent)

    return maze


def generate_maze(difficulty):
    """Генерирует лабиринт с финальной комнатой"""
    if difficulty == 'A':
        maze, last_room_id, final_room = generate_base_maze(7, 10)
        maze = add_traps(maze, last_room_id, 2, 3, final_room)
    elif difficulty == 'B':
        maze, last_room_id, final_room = generate_base_maze(11, 15)
        maze = add_traps(maze, last_room_id, 3, 5, final_room)
    elif difficulty == 'C':
        maze, last_room_id, final_room = generate_base_maze(16, 22)
        maze = add_traps(maze, last_room_id, 5, 7, final_room)
    else:
        raise ValueError("Допустимые уровни сложности: A, B, C")

    for exit in list(maze.get("room1", [])):
        if not maze.get(exit, None):
            maze["room1"].remove(exit)

    maze["_meta"] = {"final_room": final_room}
    return maze


def convert_to_json(maze):
    """Конвертирует maze в JSON с death_description для ловушек"""
    rooms = []
    final_room_id = maze.get("_meta", {}).get("final_room", "")

    for room_id, exits in maze.items():
        if room_id.startswith("_"):
            continue

        is_trap = not exits  # Ловушка не имеет выходов
        room_data = {
            "id": room_id,
            "name": "",
            "description": "",
            "room_type": "trap" if is_trap else "normal",
            "is_start": room_id == "room1",
            "exits": [{"target_room": target} for target in exits],
            "npcs": [],
            "puzzles": [],
            "treasures": []
        }

        if is_trap:
            room_data["death_description"] = ""

        if room_id == final_room_id:
            room_data["treasures"].append({
                "type": "artifact",
                "name": "",
                "description": "",
                "is_final_goal": True
            })

        rooms.append(room_data)

    return {"rooms": rooms}


def add_npcs_to_json(json_data):
    """Добавляет NPC и scroll с приоритетом ранних комнат"""
    trap_rooms = {room["id"] for room in json_data["rooms"] if room["room_type"] == "trap"}
    final_room_id = next((room["id"] for room in json_data["rooms"]
                          if any(t.get("is_final_goal", False) for t in room.get("treasures", []))), None)

    # Сортируем комнаты по порядку (room1, room2, ...)
    sorted_rooms = sorted([r for r in json_data["rooms"] if r["id"].startswith("room")],
                          key=lambda x: int(x["id"][4:]))

    # Сначала собираем все комнаты, куда можно добавить NPC
    potential_npc_rooms = []
    for room in sorted_rooms:
        if (room["room_type"] == "normal" and room["exits"] and
                room["id"] != final_room_id):
            exits_to_traps = [
                exit["target_room"] for exit in room["exits"]
                if exit["target_room"] in trap_rooms
            ]

            safe_exits = [
                exit["target_room"] for exit in room["exits"]
                if exit["target_room"] not in trap_rooms
            ]

            if exits_to_traps and safe_exits:
                potential_npc_rooms.append((room, exits_to_traps, safe_exits))

    # Добавляем NPC и соответствующие scroll в самые ранние возможные комнаты
    npc_counter = 1
    for room, exits_to_traps, safe_exits in potential_npc_rooms:
        npc_name = f"npc{npc_counter}"
        info_to_share = random.choice(safe_exits)

        # Добавляем NPC
        room["npcs"].append({
            "name": npc_name,
            "appearance": "",
            "type": "conversational",
            "behavior": "",
            "trigger_words": [],
            "patience": random.randint(3, 7),
            "information_to_share": info_to_share,
            "trap_rooms": exits_to_traps
        })

        # Находим предыдущие комнаты (сортируем по порядку)
        parent_rooms = []
        for r in sorted_rooms:
            for exit in r["exits"]:
                if exit["target_room"] == room["id"]:
                    parent_rooms.append(r)
                    break

        if parent_rooms:
            # Выбираем самую раннюю подходящую комнату
            for parent in sorted(parent_rooms, key=lambda x: int(x["id"][4:])):
                # Проверяем условия
                if (not any(t.get("is_final_goal", False)) for t in parent.get("treasures", [])) and \
                        (not any(t.get("linked_npc") == npc_name for t in parent.get("treasures", []))):

                    # Добавляем puzzle, только если его еще нет
                    if not parent["puzzles"]:
                        parent["puzzles"].append({
                            "type": "",
                            "description": "",
                            "solution": ""
                        })

                    # Добавляем scroll
                    if "treasures" not in parent:
                        parent["treasures"] = []

                    parent["treasures"].append({
                        "type": "scroll",
                        "words": [
                            {"word": "", "translation": "", "usage_examples": []},
                            {"word": "", "translation": "", "usage_examples": []}
                        ],
                        "description": "",
                        "is_final_goal": False,
                        "linked_npc": npc_name
                    })
                    npc_counter += 1
                    break

    return json_data


def add_puzzles_and_treasures(json_data):
    """Добавляет паззлы перед развилками с ловушками (в самые ранние комнаты)"""
    trap_rooms = {room["id"] for room in json_data["rooms"] if room["room_type"] == "trap"}
    final_room_id = next((room["id"] for room in json_data["rooms"]
                          if any(t.get("is_final_goal", False) for t in room.get("treasures", []))), None)

    # Сортируем комнаты по порядку
    sorted_rooms = sorted([r for r in json_data["rooms"] if r["id"].startswith("room")],
                          key=lambda x: int(x["id"][4:]))

    # Создаем карту предшественников
    room_parents = {}
    for room in sorted_rooms:
        for exit in room["exits"]:
            target = exit["target_room"]
            if target not in room_parents:
                room_parents[target] = []
            room_parents[target].append(room["id"])

    # Находим развилки с ловушками
    fork_rooms = []
    for room in sorted_rooms:
        if room["room_type"] == "normal" and room["id"] != final_room_id:
            has_trap_exits = any(exit["target_room"] in trap_rooms for exit in room["exits"])
            is_fork = len(room["exits"]) >= 3
            if has_trap_exits and is_fork:
                fork_rooms.append(room["id"])

    # Добавляем паззлы в самые ранние предыдущие комнаты
    for fork_id in fork_rooms:
        parents = room_parents.get(fork_id, [])
        # Сортируем родителей по порядку
        for parent_id in sorted(parents, key=lambda x: int(x[4:])):
            parent = next(r for r in sorted_rooms if r["id"] == parent_id)

            # Пропускаем комнаты с артефактом или уже имеющимися паззлами
            if (any(t.get("is_final_goal", False) for t in parent.get("treasures", [])) or
                    parent["puzzles"]):
                continue

            # Добавляем один паззл
            parent["puzzles"].append({
                "type": "",
                "description": "",
                "solution": ""
            })
            break  # Только в самую раннюю подходящую комнату

    return json_data


def add_guardians(json_data):
    """Добавляет guardian NPC с разной вероятностью"""
    for room in json_data["rooms"]:
        if room["room_type"] != "normal":
            continue

        has_conversational = any(npc["type"] == "conversational" for npc in room["npcs"])
        has_artifact = any(treasure.get("is_final_goal", False) for treasure in room.get("treasures", []))
        has_puzzle = len(room["puzzles"]) > 0
        has_treasure = len(room.get("treasures", [])) > 0
        has_guardian = any(npc["type"] == "guardian" for npc in room["npcs"])

        if (not has_conversational and not has_artifact and
                not has_puzzle and not has_treasure and not has_guardian):
            room["npcs"].append({
                "name": "",
                "appearance": "",
                "type": "guardian",
                "behavior": "",
                "challenge": ""
            })

        elif (not has_conversational and not has_artifact and
              (has_puzzle or has_treasure) and not has_guardian and
              random.random() < 0.5):
            room["npcs"].append({
                "name": "",
                "appearance": "",
                "type": "guardian",
                "behavior": "",
                "challenge": ""
            })

    return json_data


def package_dungeon(json_data, difficulty):
    """Упаковывает данные в окончательную структуру"""
    return {
        "reasoning": "",
        "dungeon_name": "",
        "main_quest": {
            "goal": "",
            "description": "",
            "difficulty_level": difficulty  # Просто буква A, B или C
        },
        "player_preferences": {
            "language_focus": "",
            "difficulty_level": difficulty  # Просто буква A, B или C
        },
        "rooms": json_data["rooms"]
    }

