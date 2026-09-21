import json
import time
import logging
import aiosqlite
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MemorySystem:
    def __init__(self, db_path: str = "data/memory/memory.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    importance INTEGER DEFAULT 5,
                    created_at REAL,
                    accessed_at REAL,
                    access_count INTEGER DEFAULT 0
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp REAL,
                    metadata TEXT
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    request TEXT,
                    result TEXT,
                    steps_count INTEGER,
                    duration REAL,
                    success INTEGER,
                    timestamp REAL
                )
            """)
            await db.commit()
        self._initialized = True
        logger.info("Memory system initialized")

    async def save(self, key: str, content: str, category: str = "general", importance: int = 5):
        await self.initialize()
        now = time.time()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO memories (key, content, category, importance, created_at, accessed_at) VALUES (?, ?, ?, ?, ?, ?)",
                (key, content, category, importance, now, now)
            )
            await db.commit()
        logger.debug(f"Saved memory: {key}")

    async def recall(self, query: str, limit: int = 10) -> list[dict]:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM memories WHERE content LIKE ? ORDER BY importance DESC, accessed_at DESC LIMIT ?",
                (f"%{query}%", limit)
            )
            rows = await cursor.fetchall()
            results = [dict(row) for row in rows]

            for row in results:
                await db.execute(
                    "UPDATE memories SET accessed_at = ?, access_count = access_count + 1 WHERE id = ?",
                    (time.time(), row["id"])
                )
            await db.commit()

        return results

    async def forget(self, key: str) -> bool:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM memories WHERE key = ?", (key,))
            await db.commit()
            return cursor.rowcount > 0

    async def save_conversation(self, session_id: str, role: str, content: str, metadata: dict = None):
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO conversations (session_id, role, content, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
                (session_id, role, content, time.time(), json.dumps(metadata or {}))
            )
            await db.commit()

    async def save_task_history(self, task_id: str, request: str, result: str, steps_count: int, duration: float, success: bool):
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO task_history (task_id, request, result, steps_count, duration, success, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (task_id, request, result, steps_count, duration, 1 if success else 0, time.time())
            )
            await db.commit()

    async def get_stats(self) -> dict:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM memories")
            memory_count = (await cursor.fetchone())[0]
            cursor = await db.execute("SELECT COUNT(*) FROM conversations")
            conversation_count = (await cursor.fetchone())[0]
            cursor = await db.execute("SELECT COUNT(*) FROM task_history")
            task_count = (await cursor.fetchone())[0]
            cursor = await db.execute("SELECT COUNT(*) FROM task_history WHERE success = 1")
            success_count = (await cursor.fetchone())[0]

        return {
            "memories": memory_count,
            "conversations": conversation_count,
            "tasks": task_count,
            "successful_tasks": success_count,
            "success_rate": f"{(success_count/task_count*100):.1f}%" if task_count > 0 else "N/A"
        }
