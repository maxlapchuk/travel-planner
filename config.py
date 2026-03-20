from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY: str = "eras86fd0f2bfc60acd5714fde992db26c5b479cc6a6624152c32c7r123ec7cd"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    aic_base_url: str = "https://api.artic.edu/api/v1"
    aic_cache_ttl_seconds: int = 300

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
