from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_url: str
    db_name: str
    ARCGIS_API_KEY: str
    ARCGIS_PORTAL_URL: str
    SERVICE_AREA_LAYER_URL: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()