import yaml
from jinja2 import Template
from models import Mailbox


def get_mail_instruction(user: Mailbox) -> str | bool:
    """Загружает из файла инструкцию и рендерит её"""
    with open("instructions.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    template_str = data["email_setup"]["admin_instruction"]
    template = Template(template_str)
    instruction = template.render(username=user.name, mailbox=user.mail, password=user.password)
    return instruction


if __name__ == "__main__":
    pass