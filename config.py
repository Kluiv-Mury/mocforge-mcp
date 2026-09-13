from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ldraw_library_path: str = "data/ldraw"
    leocad_executable: str = "leocad"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()