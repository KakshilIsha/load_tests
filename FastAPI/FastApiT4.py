import uvicorn
from fastapi import FastAPI
from databases import Database
import random


# Initialize the FastAPI app
app = FastAPI()

# Database URL (adjust the username, password, hostname, and database name as per your configuration)
DATABASE_URL = "postgresql://odoo:odoo@localhost:5432/odooDb15"

# Initialize the Database object
database = Database(DATABASE_URL, min_size=20, max_size=20)  # Example sizes

@app.on_event("startup")
async def startup():
    # Connect to the database
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    # Disconnect from the database
    await database.disconnect()

@app.get("/users")
async def read_users():
    # SQL query to fetch all users but limit to 10,000
    query = "SELECT * FROM load_test LIMIT 1000"

    # Execute the query
    results = await database.fetch_all(query)

    # Return the results as JSON
    return results


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
