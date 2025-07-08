from logg import log
from models import Mailbox
from tg import make_tg_report
from config import Config as cnf
from passwd import generate_password
from mail import PosteClient as poste
from sql_base import SQLiteDB as base
from email_validator import validate_email
from ldap import get_mail_users, get_conn, set_email

config = cnf()
db = base()


ldap = config.config["ldap"]["server"]
user = config.config["ldap"]["user"]
passwd = config.config["ldap"]["passwd"]
search_base = config.config["ldap"]["search_base"]
base_dn = config.config["ldap"]["base_dn"]
mail_domain = config.config["poste"]["mail_domain"]



def check_deleted_users_from_group():
    """Смотрит кого удалили из группы Mail и отключает их почтовые ящики в Poste."""
    conn = get_conn(ldap, user, passwd)
    client = poste(
        address=config.config["poste"]["address"],
        password=config.config["poste"]["password"],
        domain=config.config["poste"]["domain"],
        verify_ssl=False
    )

    log("\n-------\nПроверка тех, кого удалили с LDAP группы mail...\n")

    # Получаем текущих пользователей из группы
    mail_users = get_mail_users(search_base, conn)

    unprocessing_users = []
    disabled_users = []

    for mail_user in mail_users:
        if not mail_user.is_active:
            disabled_users.append(mail_user)
        unprocessing_users.append(mail_user.login)

    # Находим тех, кто есть в базе, но нет в группе
    users_deleted_from_group = db.get_users_not_in_list(unprocessing_users)
    
    log(f"В группе LDAP сейчас {len(unprocessing_users)} юзеров, "
        f"в базе {len(db.get_all_active_users())}, из них деактивированных - {len(disabled_users)}, "
        f"надо снести ящики {len(users_deleted_from_group)} челам")

    # Обрабатываем удалённых пользователей
    mail_domain = config.config["poste"]["mail_domain"]
    for db_user in users_deleted_from_group:
        login = db_user["login"]
        mailbox = f"{login.lower()}@{mail_domain}"

        if db.is_user_disabled(login):
            if not client.mailbox_exists(mailbox):
                db.delete_user(login)
                log(f"{mailbox} - ящик уже удалён или не существовал, сносим...")
                continue
            log(f"Ящик {mailbox} уже отключён на основе данных локальной БД")
            continue

        if client.mailbox_exists(mailbox):
            try:
                client.update_mailbox(mailbox_id=mailbox, disabled=True)
                log(f"{mailbox} - отключили почтовый ящик Poste для пользователя, удалённого из группы mail")
                db.disable_user(login)
            except Exception as e:
                log(f"{mailbox} - не удалось отключить ящик: {e}")
        else:
            log(f"{mailbox} - ящик уже удалён или не существовал")
            db.delete_user(login)

    conn.unbind()

"""
Смотрим кто есть в группе mail, но у кого нету почтового ящика, создаём
TODO: присылание в тг
"""

def check_for_new_users():
    client = poste(
        address = config.config["poste"]["address"],
        password = config.config["poste"]["password"],
        domain = config.config["poste"]["domain"],
        verify_ssl = False
        )
    conn = get_conn(ldap, user, passwd)
    mail_users = get_mail_users(search_base, conn)

    for mail_user in mail_users:
        handle_user(client, conn, mail_user)

def handle_user(client, conn, mail_user):
    domain = mail_domain
    mailbox = f"{mail_user.login.lower()}@{domain}"

    if not client.is_valid_mailbox_login(mail_user.login):
        log(f"Бро, плохой логин '{mail_user.login}', пропускаю...")
        return

    if client.mailbox_exists(mailbox):
        handle_existing_mailbox(client, mailbox, mail_user.is_active)
    elif mail_user.is_active:
        result = create_new_mailbox(client, db, conn, mail_user, domain)
        if result:
            make_tg_report(result)
        

def handle_existing_mailbox(client, mailbox, is_active):
    if is_active and client.is_mailbox_disabled(mailbox):
        try:
            client.update_mailbox(mailbox_id=mailbox, disabled=False)
            log(f"{mailbox} - включили почтовый ящик")
        except Exception as e:
            log(f"{mailbox} не удалось включить: {e}")
    elif not is_active:
        try:
            client.update_mailbox(mailbox_id=mailbox, disabled=True)
            log(f"{mailbox} - отключили почтовый ящик")
        except Exception as e:
            log(f"{mailbox} не удалось отключить: {e}")
    else:
        log(f"{mailbox} уже существует и в порядке, пропускаю!")

def create_new_mailbox(client, db, conn, mail_user, domain) -> Mailbox | bool:

    result = {}

    mailbox = f"{mail_user.login.lower()}@{domain}"

    passwd = generate_password()

    try:
        validate_email(mailbox)
        log(f"Создаю почтовый ящик для ... {mailbox}")

        result = client.create_mailbox(
            name=mail_user.cn,
            email_prefix=mail_user.login,
            password=passwd,
            domain=domain
            )
        
        if not result:
            log(f"Не получилось создать - {mailbox} ...")
            return
        
        db.register_user(mail_user.login)

        set_email(base_dn, conn, mail_user.login, mailbox)

        log(f"Ящик создан! - {mailbox}\n-------\n")

        result = Mailbox(
            name = mail_user.cn,
            mail = mailbox,
            password = passwd
            )
        return result
    except Exception as e:
        log(f"{mailbox} - не получилось создать: {e}")
        return False

if __name__ == "__main__":
    s = check_deleted_users_from_group()
    # finish_log()