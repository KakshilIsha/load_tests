import msgspec
import uvloop
from redis.asyncio import Redis, ConnectionPool
from litestar import Litestar, get
from typing import Optional, List, Any

# Global Redis client and connection pool
redis_client: Optional[Redis] = None
redis_pool: Optional[ConnectionPool] = None


# Define msgspec models for the JSON structure
class Choice(msgspec.Struct):
    display_title: str
    display_order: int
    value: Any  # Allow any type (int, str, null, etc.)


class Field(msgspec.Struct):
    key: str
    title: str
    placeholder_text: str
    default_value: str
    helper_text: str
    should_call_api: bool
    is_marketing_tracked: bool
    display_order: int
    prefix: str
    suffix: str
    comments: str
    should_display: bool
    should_display_title: bool
    type: str
    choices: Optional[List[Choice]]
    section_id: int


class Section(msgspec.Struct):
    title: str
    should_display_title: bool
    section_display_order: int
    sub_title: bool
    is_replicable: bool
    fields_list: List[Field]
    groups_list: Optional[List]  # Adjust according to the actual type
    id: int


class Page(msgspec.Struct):
    page_type: str
    title: str
    should_display_title: bool
    page_number: int
    sub_title: str
    pre_section_message: str
    post_section_message: str
    sections_list: List[Section]


class StepData(msgspec.Struct):
    form_id: int
    title: str
    description: str
    action_url: str
    action_method: str
    pages: List[Page]


class Data(msgspec.Struct):
    step_data: StepData
    step_id: Optional[str]  # Adjust to actual type (str or int)


class Response(msgspec.Struct):
    msg: str
    msgid: str
    data: Data


async def on_startup() -> None:
    """Initialize the Redis connection pool once when the app starts."""
    global redis_client, redis_pool
    redis_pool = ConnectionPool(host='3.110.70.122', port=6379, db=0, max_connections=100)
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
        try:
            # Decode the Redis value using msgspec (high-performance JSON parser)
            value_dict = msgspec.json.decode(value, type=Response)
            # Perform key replacements efficiently
            for page in value_dict.data.step_data.pages:
                for section in page.sections_list:
                    for field in section.fields_list:
                        field.default_value = field.key
            return {"data": value_dict}
        except msgspec.DecodeError as e:
            return {"error": "Failed to parse JSON"}

    return {"data": None}


# Configure Litestar app with optimizations
app = Litestar(
    route_handlers=[get_value_from_redis],
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
    debug=False,  # Explicitly disable debug mode for better performance
    listeners=[],
)

