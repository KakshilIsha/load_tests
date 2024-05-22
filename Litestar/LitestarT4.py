from __future__ import annotations
from typing import TYPE_CHECKING
from litestar import Controller, Litestar, get
from litestar_asyncpg import AsyncpgConfig, AsyncpgPlugin, PoolConfig


if TYPE_CHECKING:
    from asyncpg import Connection

class SampleController(Controller):
    @get(path="/users")
    async def sample_route(self, db_connection: Connection) -> dict[str, str]:
        result = await db_connection.fetch("SELECT * FROM load_test LIMIT 1000")
        users = [dict(record) for record in result]
        return {"data": users}


asyncpg = AsyncpgPlugin(config=AsyncpgConfig(pool_config=PoolConfig(dsn="postgresql://odoo:odoo@localhost:5432/odooDb15")))
app = Litestar(plugins=[asyncpg], route_handlers=[SampleController])
