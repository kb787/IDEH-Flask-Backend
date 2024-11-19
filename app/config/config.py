import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    postgres_connection_string = os.getenv("pg_connection_string")
    track_modifications = False


class AlchemyConfig:
    alchemy_config = "sqlite:///oauth.db"
    track_modifications = False
