import os
from pathlib import Path
from typing import Final, Optional, Union, List

from dotenv import find_dotenv, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv(raise_error_if_not_found=True))

LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "DEBUG")
PROJECT_NAME: Final[str] = os.getenv("PROJECT_NAME", "Test")
LOGGING_FORMAT: Final[str] = "%(asctime)s %(name)s %(levelname)s -> %(message)s"
LOGGING_DATETIME_FORMAT: Final[str] = "%Y.%m.%d %H:%M"


_PathLike = Union[str, Path, os.PathLike[str]]


def root_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def path(*paths: _PathLike, base_path: Optional[_PathLike] = None) -> str:
    if base_path is None:
        base_path = root_dir()

    return os.path.join(base_path, *paths)


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DB_",
        extra="ignore",
    )

    uri: str = Field(default="")
    name: str = Field(default="")
    password: Optional[str] = None
    user: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None

    @property
    def url(self) -> str:
        if "sqlite" in self.uri:
            return self.uri.format(self.name)

        return self.uri.format(
            self.user, self.password, self.host, self.port, self.name
        )


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="REDIS_",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 6379


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="BOT_",
        extra="ignore",
    )

    token: str = Field(default="")
    parse_mode: Optional[str] = "HTML"
    disable_web_page_preview: Optional[bool] = True
    protect_content: Optional[bool] = None


class AdminSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ADMIN_",
        extra="ignore",
    )

    list: List[int] = []


class Settings(BaseSettings):
    db: DBSettings
    redis: RedisSettings
    bot: BotSettings
    admin: AdminSettings


def load_settings(
    db_settings: Optional[DBSettings] = None,
    redis_settings: Optional[RedisSettings] = None,
    bot_settings: Optional[BotSettings] = None,
    admin_settings: Optional[AdminSettings] = None,
) -> Settings:
    return Settings(
        db=db_settings or DBSettings(),
        redis=redis_settings or RedisSettings(),
        bot=bot_settings or BotSettings(),
        admin=admin_settings or AdminSettings(),
    )
