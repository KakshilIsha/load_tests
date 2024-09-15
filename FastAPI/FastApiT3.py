from fastapi import FastAPI, HTTPException, Depends
from fastapi import Request
import asyncpg
import orjson
from typing import Dict, Any

# Static username and password for validation
STATIC_USERNAME = "isha"
STATIC_PASSWORD = "password"

# PostgreSQL database URL
DATABASE_URL = "postgresql://postgres:ishapostgres@3.110.66.116:5432/postgres"

# Create FastAPI app
app = FastAPI()

# Create a global database connection pool
@app.on_event("startup")
async def on_startup():
    app.state.db = await asyncpg.create_pool(DATABASE_URL, min_size=50, max_size=100)

@app.on_event("shutdown")
async def on_shutdown():
    await app.state.db.close()


# Helper function to calculate the average of col9 efficiently in SQL
async def calculate_average_col9(connection):
    query = """
    SELECT AVG(col9) AS avg_col9
    FROM read_table
    LIMIT 1000;
    """
    row = await connection.fetchrow(query)
    return row['avg_col9']


# Dependency to get the database connection pool
async def get_db(request: Request):
    return request.app.state.db


# POST route for /test3 with static validation
@app.post("/test3/")
async def submit_data(data: Dict[str, str], db=Depends(get_db)):
    # Extract username and password from request
    username = data.get("username")
    password = data.get("password")

    # Static validation for username and password
    if username != STATIC_USERNAME or password != STATIC_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # SQL query for insertion
    write_query = """
    INSERT INTO write_table (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10) 
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    RETURNING id;
    """

    async with db.acquire() as connection:
        # Calculate the average of col9
        average_col9 = await calculate_average_col9(connection)

        # Fetch one row for example data
        row = await connection.fetchrow("""
        SELECT col1, col2, col3, col4, col5, col10, col2, col3, col15::jsonb
        FROM read_table
        LIMIT 1;
        """)

        # Insert using efficient prepared statements
        await connection.execute(
            write_query,
            row['col1'],  # col1: VARCHAR(255) to col1
            row['col2'],  # col2: INTEGER to col2
            row['col3'],  # col3: DECIMAL to col3
            row['col4'],  # col4: TEXT to col4
            row['col5'],  # col5: BOOLEAN to col5
            row['col10'],  # col10 (VARCHAR) from read_table mapped to col6 (VARCHAR)
            row['col2'],  # col2 (INTEGER) from read_table mapped to col7 (INTEGER)
            row['col3'],  # col3 (DECIMAL) from read_table mapped to col8 (DECIMAL)
            str(average_col9),  # col9: Average of INTEGER mapped to col9 (TEXT)
            row['col15']  # Decode bytes to string for col10 (JSONB)
        )

    return {"message": "Success", "status": "ok"}
