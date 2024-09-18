from litestar import Litestar, get
from litestar.datastructures import State
import asyncpg
import random
import decimal
from typing import Dict, Any
import json
# PostgreSQL database URL
DATABASE_URL = "postgresql://postgres:ishapostgres@13.235.64.40:5432/postgres"

# Helper function to handle Decimal serialization
def decimal_to_float(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

# Application startup event to create connection pool
async def on_startup(app: Litestar) -> None:
    app.state.db = await asyncpg.create_pool(DATABASE_URL, min_size=20, max_size=50)

# Application shutdown event to close the connection pool
async def on_shutdown(app: Litestar) -> None:
    await app.state.db.close()

# Highly optimized route
@get("/test2/")
async def query_data(state: State, value: int) -> Dict[str, Any]:
    # Query with a condition on col2 and limit 100 rows
    query = """
    SELECT col1, col2, col3, col4, col5, col6, col7, col8, col9, col10,
           col11, col12, col13, col14, col15::jsonb 
    FROM read_table 
    WHERE col2 < $1 
    LIMIT 100;
    """

    async with state.db.acquire() as connection:
        # Execute the query and fetch results
        rows = await connection.fetch(query, value)

    # Convert rows to dictionaries and modify data
    result = []
    for row in rows:
        row_dict = dict(row)
        row_dict["col2"] = random.randint(1, 1000)  # Modify some values
        json_data = json.loads(row_dict["col15"])
        json_data["key_1"] = "UpdatedValue"
        row_dict["col15"] = json_data
        result.append(row_dict)

    return {"data": result}


# Create the Litestar app with lifecycle events
app = Litestar(
    route_handlers=[query_data],
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
    debug=False  # Explicitly disable debug mode
)
