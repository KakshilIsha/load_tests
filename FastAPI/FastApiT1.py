import uvicorn
from fastapi import FastAPI

# Initialize the FastAPI app
app = FastAPI()

@app.get("/users")
async def read_users():
    ##Create a dummy json of users with random data - 100 users, id, name & description
    users = []
    for i in range(100):
        user = {
            "id": i,
            "name": f"User {i}",
            "description": f"Description {i}"
        }
        users.append(user)
    return users


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
