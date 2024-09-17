import uvicorn
from fastapi import FastAPI, HTTPException
import asyncpg
import orjson
import random
import decimal

# Initialize the FastAPI app
app = FastAPI(docs_url=None, redoc_url=None, debug=False)

# PostgreSQL database URL
DATABASE_URL = "postgresql://postgres:ishapostgres@3.110.140.138:5432/postgres"


@app.on_event("startup")
async def startup():
    # Create a connection pool
    app.state.db = await asyncpg.create_pool(DATABASE_URL, min_size=20, max_size=50)

@app.on_event("shutdown")
async def shutdown():
    # Close the database connection pool
    await app.state.db.close()

# Helper function to handle Decimal serialization
def decimal_to_float(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

# Highly optimized route
@app.get("/test2/")
async def query_data(value: int):
    # Query with a condition on col2 and limit 100 rows
    query = """
    SELECT col1, col2, col3, col4, col5, col6, col7, col8, col9, col10,
           col11, col12, col13, col14, col15::jsonb 
    FROM read_table 
    WHERE col2 < $1 
    LIMIT 100;
    """

    async with app.state.db.acquire() as connection:
        # Execute the query and fetch results
        rows = await connection.fetch(query, value)

    # Convert rows to dictionaries and modify data
    result = []
    for row in rows:
        row_dict = dict(row)
        row_dict["col2"] = random.randint(1, 1000)  # Modify some values
        json_data = orjson.loads(row_dict["col15"])
        json_data["key_1"] = "UpdatedValue"
        row_dict["col15"] = json_data
        result.append(row_dict)

    return {"data": result}

