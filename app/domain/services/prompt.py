# app/domain/services/prompt.py
from typing import List, Optional
from sqlmodel import Session
from fastapi import Depends
from app.domain.models.prompt import PromptCreate, PromptRead, PromptUpdate
from app.infrastructure.database.repositories.prompt import PromptRepository
from app.infrastructure.database.db import get_db

class PromptService:
    def __init__(self, db: Session = Depends(get_db)):
        self.prompt_repository = PromptRepository(db)

    async def create_prompt(self, id: str, editable_part: str, fixed_part: str) -> PromptRead:
        prompt_create = PromptCreate(id=id, editable_part=editable_part, fixed_part=fixed_part)
        return await self.prompt_repository.add(prompt_create)

    async def get_prompt(self, prompt_id: str) -> Optional[PromptRead]:
        return await self.prompt_repository.get(prompt_id)

    async def list_prompts(self) -> List[PromptRead]:
        return await self.prompt_repository.list()

    async def update_prompt(self, prompt_id: str, editable_part: Optional[str], fixed_part: Optional[str]) -> Optional[PromptRead]:
        prompt_update = PromptUpdate(editable_part=editable_part, fixed_part=fixed_part)
        return await self.prompt_repository.update(prompt_id, prompt_update)
