SCHEMA = {
    "type": "object",
    "properties": {
        "dungeon_name": {"type": "string"},
        "main_quest": {
            "type": "object",
            "properties": {
                "goal": {"type": "string"},
                "description": {"type": "string"},
                "difficulty_level": {"type": "string"}
            },
            "required": ["goal", "description", "difficulty_level"]
        },
        "player_preferences": {
            "type": "object",
            "properties": {
                "language_focus": {"type": "string"},
                "difficulty_level": {"type": "string"}
            },
            "required": ["language_focus", "difficulty_level"]
        },
        "rooms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "room_type": {"type": "string", "enum": ["normal", "trap"]},
                    "is_start": {"type": "boolean"},
                    "exits": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "target_room": {"type": "string"},
                                "unlock_condition": {"type": "string"}
                            },
                            "required": ["target_room"]
                        }
                    },
                    "npcs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "appearance": {"type": "string"},
                                "type": {"type": "string"},
                                "behavior": {"type": "string"},
                                "challenge": {"type": "string"},
                                "trigger_words": {"type": "array"},
                                "patience": {"type": "number"},
                                "information_to_share": {"type": "string"},
                                "trap_rooms": {"type": "array"}
                            },
                            "required": ["name", "type", "behavior"]
                        }
                    },
                    "puzzles": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "description": {"type": "string"},
                                "solution": {"type": "string"}
                            },
                            "required": ["type", "description", "solution"]
                        }
                    },
                    "treasures": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "name": {"type": "string"},
                                "description": {"type": "string"},
                                "words": {"type": "array"},
                                "is_final_goal": {"type": "boolean"},
                                "linked_npc": {"type": "string"}
                            },
                            "required": ["type", "description"]
                        }
                    },
                    "death_description": {"type": "string"}
                },
                "required": ["id", "name", "description", "room_type", "exits"]
            }
        }
    },
    "required": ["dungeon_name", "main_quest", "rooms", "player_preferences"]
}