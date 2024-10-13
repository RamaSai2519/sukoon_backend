import os
from configs.dev_config import DevConfig
from configs.main_config import MainConfig
from configs.local_config import LocalConfig


ENV = os.environ.get('ENV')

if ENV == 'main':
    CONFIG = MainConfig
elif ENV == 'local':
    CONFIG = LocalConfig
    print(f'\n!!! Server started in LOCAL environment !!!\n')
else:
    CONFIG = DevConfig
    print(f'\n!!! Server started in DEV environment !!!\n')
