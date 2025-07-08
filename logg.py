import os
from datetime import datetime

def log(message: str) -> None:
    """
    Записывает сообщение в лог-файл latest.log и выводит в консоль.
    Формат: [YYYY-MM-DD HH:MM:SS]: сообщение
    """
    # Текущая дата и время
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")  # Для лога с секундами

    # Формируем сообщение
    log_message = f"[{timestamp}]: {message}"

    # Создаём папку ./logs, если её нет
    log_dir = "./logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Имя файла лога — всегда latest.log
    log_file = f"{log_dir}/latest.log"

    # Записываем в файл с новой строки
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    except Exception as e:
        print(f"Ошибка при записи в лог: {e}")

    # Выводим в консоль
    print(log_message)

def finish_log() -> str | None:
    """
    Переименовывает latest.log в log_YYYY-MM-DD_HH-MM.txt с текущей датой и временем.
    """
    now = datetime.now()
    file_timestamp = now.strftime("%Y-%m-%d_%H-%M")  # Для имени файла без секунд

    log_dir = "./logs"
    current_log = f"{log_dir}/latest.log"
    new_log = f"{log_dir}/log_{file_timestamp}.txt"

    # Проверяем, существует ли latest.log, и переименовываем
    try:
        if os.path.exists(current_log):
            os.rename(current_log, new_log)
            return new_log
        else:
            pass
    except Exception as e:
        return None

if __name__ == "__main__":
    pass