import sqlite3
from datetime import datetime
from logg import log

class SQLiteDB:
    def __init__(self, db_name="base.db"):
        """Инициализация базы данных и создание таблицы, если её нет."""
        self.db_name = db_name
        self._create_table()

    def _create_table(self):
        """Создание таблицы users, если она не существует."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_at TEXT NOT NULL,
                        login TEXT NOT NULL,
                        disabled INTEGER NOT NULL DEFAULT 0
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            log(f"Ошибка при создании таблицы: {e}")
    
    def is_user_disabled(self, login: str) -> bool:
        """Проверяет, отключён ли пользователь с заданным логином."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT disabled FROM users WHERE login = ?", (login,))
                result = cursor.fetchone()

                return result[0] == 1 if result else False
        except sqlite3.Error as e:
            log(f"Ошибка при проверке статуса пользователя: {e}")
            return False
    
    def register_user(self, login: str) -> bool:
        """Регистрирует нового пользователя с заданным логином. Возвращает True, если успешно."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
                if cursor.fetchone():
                    log(f"Пользователь с логином '{login}' уже существует.")
                    return False
                

                current_time = datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO users (created_at, login, disabled) VALUES (?, ?, ?)",
                    (current_time, login, 0)  # disabled = 0 значит False
                )
                conn.commit()
                log(f"Пользователь '{login}' успешно зарегистрирован в локалькой БД!")
                return True
        except sqlite3.Error as e:
            log(f"Ошибка при регистрации пользователя: {e}")
            return False
    
    def user_exists(self, login: str) -> bool:
        """Проверяет, существует ли пользователь с заданным логином."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE login = ?", (login,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            log(f"Ошибка при проверке существования пользователя: {e}")
            return False

    def get_all_active_users(self) -> list[str]:
        """Возвращает список логинов всех активных пользователей (disabled = 0)."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT login FROM users WHERE disabled = 0")
                # Извлекаем все логины в список
                result = cursor.fetchall()
                return [row[0] for row in result]  # Преобразуем кортежи в список строк
        except sqlite3.Error as e:
            log(f"Ошибка при получении активных пользователей 1: {e}")
            return []
    
    def get_users_not_in_list(self, logins: list[str]) -> list[dict]:
        """Возвращает всех пользователей, чьи логины не входят в переданный список."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                conn.row_factory = sqlite3.Row  # Чтобы возвращать словари
                cursor = conn.cursor()
                # Преобразуем список логинов в строку для NOT IN
                placeholders = ','.join('?' for _ in logins)
                query = f"SELECT * FROM users WHERE login NOT IN ({placeholders})"
                cursor.execute(query, logins)
                result = cursor.fetchall()
                return [dict(row) for row in result]  # Преобразуем строки в словари
        except sqlite3.Error as e:
            log(f"Ошибка при получении пользователей 2: {e}")
            return []

    def disable_user(self, login: str) -> bool:
        """Отключает пользователя с заданным логином (устанавливает disabled = 1)."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET disabled = 1 WHERE login = ?", (login,))
                conn.commit()
                if cursor.rowcount > 0:
                    log(f"Пользователь '{login}' отключён в локальной БД")
                    return True
                else:
                    log(f"Пользователь '{login}' не найден в БД для отключения")
                    return False
        except sqlite3.Error as e:
            log(f"Ошибка при отключении пользователя '{login}': {e}")
            return False

    def enable_user(self, login: str) -> bool:
        """Активирует пользователя с заданным логином (устанавливает disabled = 0)."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET disabled = 0 WHERE login = ?", (login,))
                conn.commit()
                if cursor.rowcount > 0:
                    log(f"Пользователь '{login}' активирован в локальной БД")
                    return True
                else:
                    log(f"Пользователь '{login}' не найден в БД для активации")
                    return False
        except sqlite3.Error as e:
            log(f"Ошибка при активации пользователя '{login}': {e}")
            return False

    def delete_user(self, login: str) -> bool:
        """Удаляет пользователя с заданным логином из локальной БД."""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE login = ?", (login,))
                conn.commit()
                if cursor.rowcount > 0:

                    return True
                else:

                    return False
        except sqlite3.Error as e:
            log(f"Ошибка при удалении пользователя '{login}': {e}")
            return False

if __name__ == "__main__":
    db = SQLiteDB()  # создаст base.db и таблицу users, если их нет