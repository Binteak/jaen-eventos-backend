from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Jaén Eventos API"
    database_url: str = "sqlite:///./jaen_eventos.db"
    cors_origins: str = "http://localhost:4204,http://127.0.0.1:4204"
    seed_demo: bool = True
    scraper_user_agent: str = "JaenEventosBot/0.1 (contact: contacto@example.com)"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
