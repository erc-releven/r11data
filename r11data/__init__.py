from pydantic_settings import BaseSettings, SettingsConfigDict
from r11data.utils.paths import env_path


class Settings(BaseSettings):
    """Main settings class."""

    model_config = SettingsConfigDict(env_file=env_path)

    GRAPHDB_USER: str
    GRAPHDB_PASSWD: str

    WISSKI_USER: str
    WISSKI_PASSWD: str


settings = Settings()
