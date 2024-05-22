from __future__ import annotations
from litestar import Controller, Litestar, get
from typing import List, Dict


class SampleController(Controller):
    @get(path="/users")
    async def sample_route(self) -> List[Dict[str, str]]:
        users = [{"id": i, "name": f"User {i}", "description": f"Description {i}"} for i in range(100)]
        return users


app = Litestar(route_handlers=[SampleController])
