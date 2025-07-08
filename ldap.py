from config import Config as cnf
from ldap3 import Server, Connection, ALL, NTLM, SUBTREE, MODIFY_REPLACE
from models import MailUser
from logg import log


def get_conn(ldap: str, user: str, passwd: str) -> Connection:
    server = Server(ldap, get_info=ALL)
    conn = Connection(server, user, passwd, authentication=NTLM)
    return conn

def testConnection(conn: Connection) -> bool:
    try:
        conn.bind()
        log("LDAP bind ok")
        return True
    except Exception as e:
        log('LDAP Bind Failed: ', e) 
        return False

def get_mail_users(search_base: str, conn: Connection) -> list[MailUser]:
    mail_users = []

    try:
        # Поиск группы mail, чтобы получить её членов
        conn.bind()
        conn.search(
            search_base=search_base,
            search_filter='(objectClass=group)',
            attributes=['member'],
            search_scope=SUBTREE
        )
        # Получаем список членов группы
        if conn.entries:
            members = conn.entries[0].member
            for member_dn in members:
                # Для каждого члена получаем его данные + userAccountControl
                conn.search(
                    search_base=member_dn,
                    search_filter='(objectClass=user)',
                    attributes=['cn', 'givenName', 'mail', 'sAMAccountName', 'userAccountControl'],
                    search_scope=SUBTREE
                )
                
                # Проверяем, есть ли результат
                if conn.entries:
                    user = conn.entries[0]
                    # Извлекаем значение userAccountControl правильно
                    uac = 0  # Значение по умолчанию, если атрибут отсутствует
                    if hasattr(user, 'userAccountControl') and user.userAccountControl.value is not None:
                        uac = int(user.userAccountControl.value)  # Берем .value и преобразуем в int
                    is_active = not (uac & 2)  # Активен, если бит 2 не установлен

                    mail_user = MailUser(
                        cn=user.cn.value if user.cn else None,              # Извлекаем .value
                        given_name=user.givenName.value if user.givenName else None,  # Извлекаем .value
                        login=user.sAMAccountName.value if user.sAMAccountName else None,  # Извлекаем .value
                        mail=user.mail.value if user.mail else None,        # Извлекаем .value
                        is_active=is_active
                    )
                    mail_users.append(mail_user)
        
        conn.unbind()
        return mail_users

    except Exception as e:
        log(f'LDAP search failed: {e}')
        return mail_users

def set_email(search_base: str, conn: Connection, login: str, email: str) -> bool:
    """Set email field in AD"""
    try:
        if not conn.bound:
            conn.bind()
        conn.search(
            search_base=search_base,
            search_filter=f'(&(objectClass=user)(sAMAccountName={login}))',
            attributes=['distinguishedName'],
            search_scope=SUBTREE
        )
        if not conn.entries:
            log(f"Пользователь с логином {login} не найден")
            return False
        user_dn = conn.entries[0].distinguishedName.value
        changes = {'mail': [(MODIFY_REPLACE, [email])]}
        success = conn.modify(user_dn, changes)
        if success:
            log(f"Email для {login} успешно обновлён на {email}")
            return True
        else:
            log(f"Не удалось обновить email для {login}: {conn.result}")
            return False
    except Exception as e:
        log(f"Ошибка при обновлении email: {e}")
        return False

def test():
    config = cnf()

    ldap = config.config["ldap"]["server"]
    user = config.config["ldap"]["user"]
    passwd = config.config["ldap"]["passwd"]
    search_base = config.config["ldap"]["search_base"]

    conn = get_conn(ldap, user, passwd)

    users = get_mail_users(search_base, conn)

    for user in users:
        log(user.login, user.is_active)


if __name__ == "__main__":
    test()
    # pass
