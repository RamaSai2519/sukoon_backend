import os
from configs.dev_config import DevConfig
from configs.main_config import MainConfig


ENV = os.environ.get("ENV")

CONFIG = MainConfig if ENV == 'main' else DevConfig