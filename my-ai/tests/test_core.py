import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.memory.memory import MemorySystem
from core.knowledge.knowledge import KnowledgeBase


async def test_memory():
    print("=== Testing Memory System ===")
    mem = MemorySystem("data/memory/test.db")
    await mem.initialize()

    await mem.save("user_name", "User", "profile", 8)
    await mem.save("project", "MyAI Agent", "project", 7)

    results = await mem.recall("user")
    print(f"Recall 'user': {len(results)} results")

    stats = await mem.get_stats()
    print(f"Stats: {stats}")
    print("Memory test OK\n")


async def test_knowledge():
    print("=== Testing Knowledge Base ===")
    kb = KnowledgeBase("data/knowledge/test.db")
    await kb.initialize()

    doc_id = await kb.add_document(
        "Python Basics",
        "Python is a programming language. It supports classes, functions, and modules.",
        "test",
        "programming"
    )
    print(f"Added document: {doc_id}")

    results = await kb.search("programming language")
    print(f"Search results: {len(results)}")

    docs = await kb.list_documents()
    print(f"Documents: {len(docs)}")
    print("Knowledge test OK\n")


async def main():
    await test_memory()
    await test_knowledge()
    print("All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
