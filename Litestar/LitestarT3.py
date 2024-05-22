from __future__ import annotations
from typing import TYPE_CHECKING
from litestar import Controller, Litestar, get
import asyncpg

if TYPE_CHECKING:
    from asyncpg import Connection

# Database URL
DATABASE_URL = "postgresql://odoo:odoo@localhost:5432/odooDb15"

# Define the startup and shutdown event handlers
async def on_startup():
    app.state.db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=20, max_size=20)

async def on_shutdown():
    await app.state.db_pool.close()

class SampleController(Controller):
    @get(path="/users")
    async def sample_route(self) -> dict[str, str]:
        async with app.state.db_pool.acquire() as connection:
            result = await connection.fetch("SELECT * FROM load_test LIMIT 100")
            users = [dict(record) for record in result]
            return {"data": users}

# Create the Litestar app and add event handlers
app = Litestar(route_handlers=[SampleController], on_startup=[on_startup], on_shutdown=[on_shutdown])
