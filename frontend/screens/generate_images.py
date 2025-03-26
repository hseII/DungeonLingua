import pixellab
from PIL import Image
import json
import os
from secrets import *

def generate_npc_avatars(json_file_path, api_key_pixellab):
    """
        Генерация аватаров для NPC на основе JSON-файла с описанием подземелья.

        Вход:
        - json_file_path: путь к JSON-файлу с описанием подземелья.
        - api_key_pixellab: API-ключ для сервиса PixelLab.

        Выход:
        - PNG-изображения аватаров NPC, сохраненные в папке "./data/images".

        Процесс:
        1. Загрузка JSON-файла с описанием подземелья.
        2. Перебор всех NPC в комнатах.
        3. Генерация пиксельных аватаров для каждого NPC с использованием PixelLab.
        4. Сохранение изображений в формате PNG в папке "./data/images".
    """
    # Инициализация клиента PixelLab
    client = pixellab.Client(secret=api_key_pixellab)

    # Загрузка JSON-файла с описанием подземелья
    def load_dungeon_json(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Генерация изображения для NPC с использованием PixelLab
    def generate_npc_image(npc_description, output_path):
        try:
            # Описание для генерации изображения
            description = (
                f"Create a pixel art NPC portrait in NES style, inspired by Final Fantasy. "
                f"Based on the following description: {npc_description}. "
                "The art should be minimalistic, with large, visible pixels and a retro gaming vibe. "
                "Use a limited color palette."
            )

            # Генерация изображения
            response = client.generate_image_pixflux(
                description=description,
                image_size=dict(width=64, height=64),  # Размер изображения (можно увеличить до 128x128)
            )

            # Сохранение изображения
            if response and response.image:
                image = response.image.pil_image()
                image.save(output_path, format="PNG")  # Сохраняем в формате PNG для поддержки прозрачности
                print(f"Изображение сохранено как {output_path}")
            else:
                print("Ошибка: Не удалось сгенерировать изображение.")

        except Exception as e:
            print(f"Ошибка при генерации изображения: {e}")

    # Создание папки для сохранения изображений, если она не существует
    output_dir = "./data/images"
    os.makedirs(output_dir, exist_ok=True)

    # Загрузка JSON-файла
    dungeon_data = load_dungeon_json(json_file_path)

    # Проверка наличия данных о комнатах
    if "rooms" not in dungeon_data:
        print("Ошибка: В JSON отсутствуют данные о комнатах.")
        return

    # Перебор всех комнат и NPC
    for room in dungeon_data["rooms"]:
        if "npcs" in room and room["npcs"]:
            for npc in room["npcs"]:
                # Формируем описание NPC
                npc_description = (
                    f"Name: {npc['name']}, "
                    f"Appearance: {npc['appearance']}, "
                    f"Type: {npc['type']}, "
                    f"Behavior: {npc['behavior']}"
                )

                # Генерируем изображение
                output_path = os.path.join(output_dir, f"{npc['name'].replace(' ', '_').lower()}_pixel_style.png")
                generate_npc_image(npc_description, output_path)

