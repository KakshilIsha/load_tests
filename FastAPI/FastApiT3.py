import uvicorn
from fastapi import FastAPI
import asyncpg

# Initialize the FastAPI app
app = FastAPI()

# Database URL (adjust the username, password, hostname, and database name as per your configuration)
DATABASE_URL = "postgresql://odoo:odoo@localhost:5432/odooDb15"


@app.on_event("startup")
async def startup():
    # Connect to the database and store the connection pool in app state
    app.state.db = await asyncpg.create_pool(DATABASE_URL, min_size=20, max_size=20)


@app.on_event("shutdown")
async def shutdown():
    # Close the database connection pool
    await app.state.db.close()


@app.get("/users")
async def read_users():


    # SQL query to fetch all users but limit to 100
    query = "SELECT * FROM load_test LIMIT 100"

    async with app.state.db.acquire() as connection:
        # Execute the query
        results = await connection.fetch(query)

    # Return the results as JSON
    return [dict(record) for record in results]


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
