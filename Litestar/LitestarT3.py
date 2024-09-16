from litestar import Litestar, post
from litestar.datastructures import State
import asyncpg
import orjson
from typing import Dict, Any

# Static username and password for validation
STATIC_USERNAME = "isha"
STATIC_PASSWORD = "password"

# PostgreSQL database URL
DATABASE_URL = "postgresql://postgres:ishapostgres@52.66.222.58:5432/postgres"


# Application startup event to create connection pool
async def on_startup(app: Litestar) -> None:
    app.state.db = await asyncpg.create_pool(DATABASE_URL, min_size=50, max_size=100)


# Application shutdown event to close the connection pool
async def on_shutdown(app: Litestar) -> None:
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


# POST route for Test3 with static validation
@post("/test3/")
async def submit_data(state: State, data: Dict[str, str]) -> Dict[str, str]:
    # Extract username and password from request
    username = data.get("username")
    password = data.get("password")

    # Static validation for username and password
    if username != STATIC_USERNAME or password != STATIC_PASSWORD:
        return {"message": "Invalid credentials", "status": "fail"}, 401

    # If valid, continue with processing
    write_query = """
    INSERT INTO write_table (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10) 
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    RETURNING id;
    """

    async with state.db.acquire() as connection:
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
            row['col15'] # Decode bytes to string for col10 (JSONB)
        )

    return {"message": "Success", "status": "ok"}


# Create the Litestar app with lifecycle events
app = Litestar(
    route_handlers=[submit_data],
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
    debug=False  # Explicitly disable debug mode
)

