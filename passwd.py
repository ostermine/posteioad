import secrets


def generate_password(length: int = 8) -> str:
    """
    Генерирует вкусные якобы безопасные как-будто бы случайные пароли
    Я поубирал симилярные буквы и цифры которые похожу друг на друга
    Да, это менее безопасно - idk
    """
    alphabet = "abdefghkmnprstuvwxyzAEFGHMNRTWXZ" + "2347"
    specials = "!@#="
    result = ''.join(secrets.choice(alphabet) for _ in range(length))
    passwd = result + secrets.choice(specials)
    return passwd


if __name__ == "__main__":
    pass