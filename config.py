from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    ldraw_library_path: str = str(BASE_DIR / "data" / "ldraw")
    leocad_executable: str = "leocad"

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8")

settings = Settings()