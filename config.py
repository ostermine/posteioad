import os
import yaml

class Config:
    def __init__(self, config_path="config.yml"):
        self.config_path = config_path
        self.config = None
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError("Файл конфигурации не найден.")
        with open(self.config_path, "r", encoding = "utf-8") as config_file:
            self.config = yaml.safe_load(config_file)

if __name__ == "__main__":
    #example to use
    # config = Config()
    # print(config.config["bot"]["token"])
    pass