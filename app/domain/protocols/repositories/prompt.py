from typing import Protocol
from app.domain.models.prompt import PromptCreate, PromptRead

class PromptRepository(Protocol):
    async def add(self, prompt: PromptCreate) -> PromptRead:
        ...

    async def get_all(self) -> list[PromptRead]:
        ...

    async def get(self, prompt_id: str) -> PromptRead:
        ...

    async def update(self, prompt: PromptCreate) -> PromptRead:
        ...
