from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_model_config = SettingsConfigDict(
    env_file="./.env", env_ignore_empty=True, extra="ignore"
)


class DatabaseSettings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    REDIS_HOST: str
    REDIS_PORT: int

    model_config = _model_config

    @property
    def POSTGRES_URL(self):
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def REDIS_URL(self, db):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{db}"

class SecuritySettings(BaseSettings):
    JWT_SECRET: str
    JWT_ALGORITHM: str

    model_config = _model_config


class NotificationSettings(BaseSettings):
    model_config = _model_config

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

class AppSettings(BaseSettings):
    APP_NAME: str
    APP_DOMAIN: str

    model_config = _model_config

app_settings = AppSettings()  # type: ignore
db_settings = DatabaseSettings()  # type: ignore
security_settings = SecuritySettings()  # type: ignore
notification_settings = NotificationSettings()  # type: ignore


app_dir = Path(__file__).resolve().parent
TEMPLATES_FOLDER = app_dir / 'templates'
MAIL_TEMPLATES_FOLDER = TEMPLATES_FOLDER / "mail"
