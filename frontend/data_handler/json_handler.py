import json
from pathlib import Path
from jsonschema import validate
from data_handler.validation import SCHEMA


def load_and_validate(file_path: str) -> dict:
    """Загрузка и валидация JSON-структуры"""
    try:
        full_path = Path(__file__).parent.parent / file_path
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        validate(instance=data, schema=SCHEMA)
        validate_room_connections(data)
        set_starting_room(data)

        return data

    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки: {str(e)}")


def validate_room_connections(data: dict):
    """Проверка связей между комнатами"""
    room_ids = {room["id"] for room in data["rooms"]}
    for room in data["rooms"]:
        for exit_data in room["exits"]:
            if exit_data["target_room"] not in room_ids:
                raise ValueError(f"Несуществующий выход: {exit_data['target_room']}")


def set_starting_room(data: dict):
    """Установка стартовой комнаты"""
    starting_rooms = [r for r in data["rooms"] if r.get("is_start")]
    if not starting_rooms:
        raise ValueError("Стартовая комната не определена")
    data["starting_room"] = starting_rooms[0]["id"]


def find_room_by_id(dungeon_data: dict or list, room_id: str) -> dict or None:
    """Находит комнату по ID в данных подземелья."""
    rooms = []

    # Определяем источник данных
    if isinstance(dungeon_data, dict) and "rooms" in dungeon_data:
        rooms = dungeon_data["rooms"]
    elif isinstance(dungeon_data, list):
        rooms = dungeon_data
    else:
        raise ValueError("Invalid dungeon data format")

    # Поиск комнаты
    for room in rooms:
        if room.get("id") == room_id:
            return room
    return None