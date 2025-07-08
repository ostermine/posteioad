import httpx
import re

class PosteClient:

    def __init__(self, address, password, domain, verify_ssl=True):
        self.uri = f'https://{domain}/admin/api/v1'
        self.client = httpx.Client(auth=(address, password), verify=verify_ssl)
        self.admin_address = address

    def __str__(self):
        return self.uri
    
    def is_valid_mailbox_login(self, login: str) -> bool:
        """
        Проверяет, подходит ли логин для почтового ящика по упрощённому правилу:
        только a-z (регистр не важен), точки и тире.
        Логин не должен начинаться или заканчиваться точкой, иметь две точки подряд.
        """
        if not login or len(login) == 0:  # Пустой логин невалиден
            return False
        
        # Регулярка: только a-z, точки и тире
        if not re.match(r'^[a-zA-Z.-]+$', login):
            return False
        
        # Проверки на точки
        if login.startswith('.') or login.endswith('.'):  # Начинается или заканчивается точкой
            return False
        if '..' in login:  # Две точки подряд
            return False
        
        return True

    def create_mailbox(self, name: str, email_prefix: str, password: str, domain: str) -> bool:

        email = f'{email_prefix}@{domain}'
        req = {
            "name": name,
            "email": email,
            "passwordPlaintext": password,
            "disabled": False,
            "superAdmin": False
        }
        try:
            res = self.client.post(url=f'{self.uri}/boxes', json=req, timeout=(2, 10))
            if res.status_code == 201:
                return True
            elif res.status_code == 400 and 'This combination of username and domain is already in database' in res.text:
                print('This combination of username and domain is already in database')
                return False
            else:
                print(f'create_account res:{res.status_code},{res.text}')
                return False
        except httpx.RequestError as e:
            print(f'Ошибка запроса: {e}')
            return False

    def update_mailbox(self, mailbox_id: str, name: str = None, password: str = None, 
                       disabled: bool = None, super_admin: bool = None, reference_id: str = None) -> bool:
        # Формируем данные для обновления
        req = {}
        if name is not None:
            req["name"] = name
        if password is not None:
            req["passwordPlaintext"] = password
        if disabled is not None:
            req["disabled"] = disabled
        if super_admin is not None:
            req["superAdmin"] = super_admin
        if reference_id is not None:
            req["referenceId"] = reference_id

        # Отправляем запрос PATCH
        url = f'{self.uri}/boxes/{mailbox_id}'
        try:
            res = self.client.patch(url=url, json=req, timeout=(2, 10))
            
            if res.status_code == 200 or res.status_code == 204:
                return True
            else:
                print(f'update_mailbox res:{res.status_code}, {res.text}')
                return False
        except httpx.RequestError as e:
            print(f'Ошибка запроса: {e}')
            return False

    def mailbox_exists(self, email: str) -> bool:
        """Проверяет, существует ли почтовый ящик с заданным email."""
        url = f'{self.uri}/boxes/{email}'
        try:
            res = self.client.get(url=url, timeout=(2, 10))
            if res.status_code == 200:
                return True  # Ящик существует, получили JSON
            elif res.status_code == 404:
                return False  # Ящик не найден, получили HTML с 404
            else:
                print(f'mailbox_exists unexpected status: {res.status_code}, response: {res.text}')
                return False  # Неизвестный статус, считаем, что ящика нет
        except httpx.RequestError as e:
            print(f'Ошибка при проверке ящика: {e}')
            return False

    def is_mailbox_disabled(self, email: str) -> bool:
        """Проверяет, отключен ли почтовый ящик с заданным email."""
        url = f'{self.uri}/boxes/{email}'
        try:
            res = self.client.get(url=url, timeout=(2, 10))
            if res.status_code == 200:
                data = res.json()
                return data.get("disabled", False)
            elif res.status_code == 404:
                return False  # Ящик не найден, считаем, что он не отключен
            else:
                print(f'is_mailbox_disabled unexpected status: {res.status_code}, response: {res.text}')
                return False  # Неизвестный статус, считаем, что ящик не отключен
        except httpx.RequestError as e:
            print(f'Ошибка при проверке статуса ящика: {e}')
            return False


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


if __name__ == "__main__":
    pass