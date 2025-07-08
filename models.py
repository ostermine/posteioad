from dataclasses import dataclass

@dataclass
class Mailbox:
    name: str
    mail: str
    password: str

@dataclass
class Tg:
    token: str
    admin_chat: int
    log_chat: int



class MailUser:
    def __init__(self, cn, given_name, login, mail, is_active):
        self.cn = cn
        self.given_name = given_name
        self.login = login
        self.mail = mail
        self.is_active = is_active

    def __str__(self):
        return f"CN: {self.cn}, Name: {self.given_name}, Login: {self.login}, Mail: {self.mail}, Is active in AD: {self.is_active}"

    def to_dict(self):

        return {
            "cn": self.cn,
            "name": self.given_name,
            "login": self.login,
            "mail": self.mail,
            "is_active": self.is_active
        }
