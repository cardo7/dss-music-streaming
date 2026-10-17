"""
Database connection settings shared by A4 and A6.

Credentials are NOT stored in the code: they are read from the `.env` file in the
project root (see `.env.example`). If no user/password is given, Windows
authentication (Trusted_Connection) is used, which is the usual setup for a
local SQL Server instance.
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_env(path: Path = PROJECT_ROOT / ".env") -> None:
    """Minimal .env reader (KEY=VALUE per line, '#' for comments)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env()

SERVER = os.getenv("DB_SERVER", "localhost")
DATABASE = os.getenv("DB_DATABASE", "Group_ID_6_DB")
USERNAME = os.getenv("DB_USER", "")
PASSWORD = os.getenv("DB_PASSWORD", "")
DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")


def get_conn_str() -> str:
    base = f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};"
    if USERNAME:
        return base + f"UID={USERNAME};PWD={PASSWORD}"
    return base + "Trusted_Connection=yes"
