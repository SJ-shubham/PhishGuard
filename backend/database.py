import motor.motor_asyncio
from backend.config import get_settings

_settings = get_settings()

_client: motor.motor_asyncio.AsyncIOMotorClient | None = None


def get_client() -> motor.motor_asyncio.AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = motor.motor_asyncio.AsyncIOMotorClient(_settings.mongodb_uri)
    return _client


def get_db():
    return get_client()[_settings.mongodb_db]


# Convenience accessors
def users_col():
    return get_db()["users"]


def scans_col():
    return get_db()["scans"]


async def create_indexes():
    """Create MongoDB indexes on startup."""
    db = get_db()
    await db["users"].create_index("email", unique=True)
    await db["scans"].create_index("user_id")
    await db["scans"].create_index("timestamp")
    await db["scans"].create_index([("user_id", 1), ("timestamp", -1)])
