import requests
from logg import log
from config import Config
from models import Mailbox, Tg
from messages import get_mail_instruction


cnf = Config()

tg = Tg(
    token = cnf.config["tg"]["token"],
    admin_chat = cnf.config["tg"]["admin_chat_id"],
    log_chat = cnf.config["tg"]["log_chat_id"]
    )



def send_message_to_admin_chat(message: str, chat_id: str = tg.admin_chat) -> bool:
    """TODO: при неуспешной отправке - создать файлик с данными для повторной отправки"""
    url = f"https://api.telegram.org/bot{tg.token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return True
        else:
            log(f"Не 200 код ответа от ТГ АПИ - {e}")
            return False
    except Exception as e:
        log(f"Не могу отправить в ТГшку - {e}")
        return False

def send_message_to_log_chat(message: str) -> None:
    ...

def send_logfile(filepath: str, chat_id: str = tg.log_chat) -> bool:
    """
    Отправляет файл лога как вложение в Telegram-чат.
    
    Args:
        filepath: Путь к файлу лога.
        chat_id: ID чата, по умолчанию из конфига tg.log_chat.
    
    Returns:
        True, если отправка успешна, иначе False.
    """
    url = f"https://api.telegram.org/bot{tg.token}/sendDocument"
    try:
        # Открываем файл в бинарном режиме
        with open(filepath, "rb") as f:
            # Формируем multipart/form-data
            files = {"document": (filepath, f)}
            payload = {"chat_id": chat_id}
            response = requests.post(url, data=payload, files=files)
            
        if response.status_code == 200:
            return True
        else:
            return False
    except FileNotFoundError:
        log(f"Файл {filepath} не найден")
        return False
    except requests.RequestException as e:
        log(f"Ошибка запроса к Telegram API: {e}")
        return False
    except Exception as e:
        log(f"Неизвестная ошибка при отправке файла: {e}")
        return False


def make_tg_report(user: Mailbox) -> None:
    message = get_mail_instruction(user)
    send_message_to_admin_chat(message)
    log(f"Отправка в ТГ данных - {user.name} {user.mail}")


if __name__ == "__main__":
    pass