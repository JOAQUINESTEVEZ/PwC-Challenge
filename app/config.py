from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USERNAME: str = "default"
    REDIS_PASSWORD: str
    REDIS_KEY_PREFIX: str = "finapp:"
    REDIS_POOL_SIZE: int = 10
    REDIS_POOL_TIMEOUT: int = 5
    REDIS_DECODE_RESPONSES: bool = True
    REDIS_CACHE_TTL: int = 300

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        

settings = Settings()

