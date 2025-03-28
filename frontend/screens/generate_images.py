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
'''
import pixellab
from PIL import Image
import json
import os
import threading
from queue import Queue
from secrets import *


def generate_npc_avatars(json_file_path, api_key_pixellab):
    """
    Генерация аватаров для NPC на основе JSON-файла с описанием подземелья.
    Запросы на генерацию изображений выполняются асинхронно в отдельных потоках.
    """
    # Инициализация клиента PixelLab (общий для всех потоков)
    client = pixellab.Client(secret=api_key_pixellab)

    # Очередь для хранения результатов
    result_queue = Queue()

    def load_dungeon_json(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def generate_npc_image(npc_description, output_path, result_queue):
        """Функция для выполнения в потоке"""
        try:
            description = (
                f"Create a pixel art NPC portrait in NES style, inspired by Final Fantasy. "
                f"Based on: {npc_description}. "
                "Minimalistic, large visible pixels, retro gaming vibe, limited color palette."
            )

            response = client.generate_image_pixflux(
                description=description,
                image_size=dict(width=64, height=64),
            )

            if response and response.image:
                image = response.image.pil_image()
                image.save(output_path, format="PNG")
                result_queue.put((output_path, True))
            else:
                result_queue.put((output_path, False))

        except Exception as e:
            print(f"Ошибка при генерации {output_path}: {e}")
            result_queue.put((output_path, False))

    # Создание папки для изображений
    output_dir = "./data/images"
    os.makedirs(output_dir, exist_ok=True)

    # Загрузка JSON
    dungeon_data = load_dungeon_json(json_file_path)

    if "rooms" not in dungeon_data:
        print("Ошибка: В JSON отсутствуют данные о комнатах.")
        return

    # Список для хранения потоков
    threads = []

    # Перебор NPC и создание потоков
    for room in dungeon_data["rooms"]:
        if "npcs" in room and room["npcs"]:
            for npc in room["npcs"]:
                npc_description = (
                    f"Name: {npc['name']}, "
                    f"Appearance: {npc['appearance']}, "
                    f"Type: {npc['type']}, "
                    f"Behavior: {npc['behavior']}"
                )

                output_path = os.path.join(
                    output_dir,
                    f"{npc['name'].replace(' ', '_').lower()}_pixel_style.png"
                )

                # Создаем и запускаем поток для каждого NPC
                thread = threading.Thread(
                    target=generate_npc_image,
                    args=(npc_description, output_path, result_queue)
                )
                thread.start()
                threads.append(thread)

    # Ожидание завершения всех потоков
    for thread in threads:
        thread.join()

    # Обработка результатов
    success_count = 0
    failed_count = 0

    while not result_queue.empty():
        path, success = result_queue.get()
        if success:
            print(f"Успешно сгенерировано: {path}")
            success_count += 1
        else:
            print(f"Ошибка генерации: {path}")
            failed_count += 1

    print(f"\nИтог: {success_count} успешно, {failed_count} с ошибками")
'''