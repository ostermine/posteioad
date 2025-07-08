from logg import log, finish_log
from handle_users import check_for_new_users, check_deleted_users_from_group
from tg import send_logfile

def main():
    log("Старт синхронизации пользователей и почтовых ящиков")
    check_for_new_users()
    check_deleted_users_from_group()
    log("Синхронизация завершена")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"Критическая ошибка в скрипте: {e}")
    finally:
        logfile = finish_log()
        if logfile:
            send_logfile(logfile)
