from __future__ import annotations
from typing import TYPE_CHECKING
from litestar import Controller, Litestar, get
from litestar_asyncpg import AsyncpgConfig, AsyncpgPlugin, PoolConfig
import random

if TYPE_CHECKING:
    from asyncpg import Connection

class SampleController(Controller):
    @get(path="/users")
    async def sample_route(self, db_connection: Connection) -> dict[str, str]:
        random_id = random.randint(1, 600000)
        result = await db_connection.fetch("SELECT * FROM load_test where id = " + str(random_id))
        return dict(result[0])


asyncpg = AsyncpgPlugin(config=AsyncpgConfig(pool_config=PoolConfig(dsn="postgresql://odoo:odoo@localhost:5432/odooDb15")))
app = Litestar(plugins=[asyncpg], route_handlers=[SampleController])
