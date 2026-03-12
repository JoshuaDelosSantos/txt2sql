import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).parent

@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    db_name: str = os.getenv("DB_NAME", "text2sqldb")
    db_user: str = os.getenv("DB_USER", "text2sqldb_user")
    db_password: str = os.getenv("DB_PASSWORD")
    
    api_key: str = os.getenv("API_KEY")
    chat_model: str = os.getenv("CHAT_MODEL")
    
    schema_dir: Path = Path(os.environ["SCHEMA_DIR"]) if os.environ.get("SCHEMA_DIR") else ROOT_DIR / "schemas"
    
    def require_db(self) -> None:
        """Raise if DB connection setings are incimplete."""
        for field in ("db_name", "db_user", "db_password"):
            if not getattr(self, field):
                raise RuntimeError(f"Missing required DB setting: {field.upper()}")
            
    def require_llm(self) -> None:
        """Raise if LLM settings are incomplete."""
        for field in ("api_key", "chat_model"):
            if not getattr(self, field):
                raise RuntimeError(f"Missing required LLM setting: {field.upper()}")
            
settings = Settings()