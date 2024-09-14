from __future__ import annotations
from typing import TYPE_CHECKING
from litestar import Controller, Litestar, get
from litestar_asyncpg import AsyncpgConfig, AsyncpgPlugin, PoolConfig
import logging
from typing import Any, Dict
from litestar import Litestar, post
from asyncpg import Connection
from litestar.controller import Controller

if TYPE_CHECKING:
    from asyncpg import Connection


class SampleController(Controller):
    @post(path="/users")
    async def read_users_post(self, data: Dict[str, Any], db_connection: Connection) -> Dict[str, Any]:
        try:
            # Process the incoming JSON parameters
            limit = data.get('limit', 100)  # Default to 100 if not provided

            # Log the parameters
            logging.info(f"Received parameters: {data}")

            # Construct the SQL query using the parameters
            query = f"SELECT * FROM load_test LIMIT $1"

            # Execute the query
            results = await db_connection.fetch(query, limit)

            # Return the results as JSON
            users = [dict(record) for record in results]
            return {"data": users}
        except Exception as e:
            logging.error(f"Error querying database: {e}")
            return {"error": "Error querying database", "details": str(e)}


asyncpg = AsyncpgPlugin(config=AsyncpgConfig(pool_config=PoolConfig(dsn="postgresql://odoo:odoo@localhost:5432/odooDb15")))
app = Litestar(plugins=[asyncpg], route_handlers=[SampleController])
