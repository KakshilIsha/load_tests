import orjson
from redis.asyncio import Redis, ConnectionPool
from litestar import Litestar, get
from typing import Optional

# Global Redis client and connection pool
redis_client: Optional[Redis] = None
redis_pool: Optional[ConnectionPool] = None


async def on_startup() -> None:
    """Initialize the Redis connection pool once when the app starts."""
    global redis_client, redis_pool
    redis_pool = ConnectionPool(host='52.66.234.102', port=6379, db=0, max_connections=20)
    redis_client = Redis(connection_pool=redis_pool)


async def on_shutdown() -> None:
    """Close the Redis connection pool when the app shuts down."""
    if redis_client:
        await redis_client.close()
    if redis_pool:
        await redis_pool.disconnect()


@get("/test1")
async def get_value_from_redis() -> dict:
    value = await redis_client.get('TestJSON')
    if value:
        # Decode using orjson for faster performance
        value_dict = orjson.loads(value)

        # Perform the loop optimizations and key replacements in one pass
        for page in value_dict['data']['step_data']['pages']:
            for section in page['sections_list']:
                for field in section['fields_list']:
                    field['default_value'] = field.get('key', None)  # Use get for robustness

        return {"data": value_dict}

    return {"data": None}


# Configuring the Litestar app with startup and shutdown events
app = Litestar(
    route_handlers=[get_value_from_redis],
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
    debug=False  # Explicitly disable debug mode
)
