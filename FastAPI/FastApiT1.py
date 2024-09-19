import uvloop
from redis.asyncio import Redis, ConnectionPool
from fastapi import FastAPI
from typing import Optional, List, Any

# Global Redis client and connection pool
redis_client: Optional[Redis] = None
redis_pool: Optional[ConnectionPool] = None

# Define Pydantic models for the JSON structure
from pydantic import BaseModel


class Choice(BaseModel):
    display_title: str
    display_order: int
    value: Any  # Allow any type (int, str, null, etc.)


class Field(BaseModel):
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


class Section(BaseModel):
    title: str
    should_display_title: bool
    section_display_order: int
    sub_title: bool
    is_replicable: bool
    fields_list: List[Field]
    groups_list: Optional[List]  # Adjust according to the actual type
    id: int


class Page(BaseModel):
    page_type: str
    title: str
    should_display_title: bool
    page_number: int
    sub_title: str
    pre_section_message: str
    post_section_message: str
    sections_list: List[Section]


class StepData(BaseModel):
    form_id: int
    title: str
    description: str
    action_url: str
    action_method: str
    pages: List[Page]


class Data(BaseModel):
    step_data: StepData
    step_id: Optional[str]  # Adjust to actual type (str or int)


class Response(BaseModel):
    msg: str
    msgid: str
    data: Data


# FastAPI app initialization
app = FastAPI()


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


# Set startup and shutdown events in FastAPI
@app.on_event("startup")
async def startup_event():
    await on_startup()


@app.on_event("shutdown")
async def shutdown_event():
    await on_shutdown()


@app.get("/test1")
async def get_value_from_redis() -> dict:
    value = await redis_client.get('TestJSON')
    if value:
        try:
            # Decode the Redis value using Pydantic models
            value_dict = Response.parse_raw(value)

            # Perform key replacements efficiently
            for page in value_dict.data.step_data.pages:
                for section in page.sections_list:
                    for field in section.fields_list:
                        field.default_value = field.key

            return {"data": value_dict.dict()}  # Return as a dict that FastAPI will convert to JSON

        except Exception as e:
            return {"error": f"Failed to parse JSON: {str(e)}"}

    return {"data": None}


