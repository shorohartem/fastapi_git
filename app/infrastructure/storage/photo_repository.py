import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


class PhotoRepository:
    def __init__(self, media_root: str):
        self.media_root = Path(media_root).resolve()
        self.upload_root = self.media_root / "uploads"
        self.database_path = self.media_root / "photos.sqlite3"
        self.upload_root.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS photos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    storage_path TEXT NOT NULL UNIQUE,
                    original_filename TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def create(
        self,
        contents: bytes,
        suffix: str,
        original_filename: str,
        content_type: str,
    ) -> dict:
        storage_path = f"uploads/{uuid4().hex}{suffix}"
        absolute_path = self.media_root / storage_path
        absolute_path.write_bytes(contents)
        created_at = datetime.now(timezone.utc).isoformat()

        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO photos (
                        storage_path, original_filename, content_type, created_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (storage_path, original_filename, content_type, created_at),
                )
                photo_id = cursor.lastrowid
        except Exception:
            absolute_path.unlink(missing_ok=True)
            raise

        return self.get(photo_id)

    def get(self, photo_id: int) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, storage_path, original_filename, content_type, created_at
                FROM photos
                WHERE id = ?
                """,
                (photo_id,),
            ).fetchone()
        return dict(row) if row else None
