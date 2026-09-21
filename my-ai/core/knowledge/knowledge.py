import json
import time
import logging
import aiosqlite
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class KnowledgeBase:
    def __init__(self, db_path: str = "data/knowledge/knowledge.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT,
                    category TEXT DEFAULT 'general',
                    tags TEXT DEFAULT '[]',
                    created_at REAL,
                    updated_at REAL
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS search_index (
                    doc_id INTEGER,
                    term TEXT,
                    tf REAL,
                    FOREIGN KEY (doc_id) REFERENCES documents(id)
                )
            """)
            await db.commit()
        self._initialized = True
        logger.info("Knowledge base initialized")

    async def add_document(self, title: str, content: str, source: str = "", category: str = "general", tags: list = None):
        await self.initialize()
        now = time.time()
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO documents (title, content, source, category, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title, content, source, category, json.dumps(tags or []), now, now)
            )
            doc_id = cursor.lastrowid

            terms = self._tokenize(content)
            term_freq = {}
            for term in terms:
                term_freq[term] = term_freq.get(term, 0) + 1

            for term, freq in term_freq.items():
                tf = freq / len(terms) if terms else 0
                await db.execute(
                    "INSERT INTO search_index (doc_id, term, tf) VALUES (?, ?, ?)",
                    (doc_id, term, tf)
                )

            await db.commit()
        logger.debug(f"Added document: {title}")
        return doc_id

    async def search(self, query: str, limit: int = 5) -> list[dict]:
        await self.initialize()
        query_terms = self._tokenize(query)

        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row

            placeholders = ",".join("?" * len(query_terms))
            cursor = await db.execute(f"""
                SELECT d.*, SUM(si.tf) as relevance
                FROM documents d
                JOIN search_index si ON d.id = si.doc_id
                WHERE si.term IN ({placeholders})
                GROUP BY d.id
                ORDER BY relevance DESC
                LIMIT ?
            """, query_terms + [limit])

            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_document(self, doc_id: int) -> Optional[dict]:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def list_documents(self, category: str = None, limit: int = 50) -> list[dict]:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if category:
                cursor = await db.execute(
                    "SELECT id, title, category, created_at FROM documents WHERE category = ? ORDER BY created_at DESC LIMIT ?",
                    (category, limit)
                )
            else:
                cursor = await db.execute(
                    "SELECT id, title, category, created_at FROM documents ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def delete_document(self, doc_id: int) -> bool:
        await self.initialize()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM search_index WHERE doc_id = ?", (doc_id,))
            cursor = await db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            await db.commit()
            return cursor.rowcount > 0

    def _tokenize(self, text: str) -> list[str]:
        import re
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        tokens = text.split()
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                       "have", "has", "had", "do", "does", "did", "will", "would", "could",
                       "should", "may", "might", "shall", "can", "to", "of", "in", "for",
                       "on", "with", "at", "by", "from", "as", "into", "about", "this",
                       "that", "these", "those", "it", "its", "and", "or", "but", "not"}
        return [t for t in tokens if t not in stop_words and len(t) > 1]
