import os
from dotenv import load_dotenv

def load_environment():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    env_path = os.path.join(base_dir, '.env')
    load_dotenv(dotenv_path=env_path)
