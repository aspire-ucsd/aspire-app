# app/infrastructure/database/repositories/prompt.py
from typing import List, Optional
from sqlmodel import Session
from fastapi import Depends
from app.domain.models.prompt import Prompt, PromptCreate, PromptRead, PromptUpdate
from app.infrastructure.database.db import get_db

class PromptRepository:
    db: Session
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    async def add(self, prompt_create: PromptCreate) -> PromptRead:
        prompt = Prompt.from_orm(prompt_create)
        self.db.add(prompt)
        self.db.commit()
        self.db.refresh(prompt)
        return PromptRead.from_orm(prompt)

    async def get(self, prompt_id: str) -> Optional[PromptRead]:
        prompt = self.db.get(Prompt, prompt_id)
        if prompt:
            return PromptRead.from_orm(prompt)
        return None

    async def list(self) -> List[PromptRead]:
        prompts = self.db.query(Prompt).all()
        return [PromptRead.from_orm(prompt) for prompt in prompts]

    async def update(self, prompt_id: str, prompt_update: PromptUpdate) -> Optional[PromptRead]:
        prompt = self.db.get(Prompt, prompt_id)
        if prompt:
            if prompt_update.editable_part is not None:
                prompt.editable_part = prompt_update.editable_part
            if prompt_update.fixed_part is not None:
                prompt.fixed_part = prompt_update.fixed_part
            self.db.add(prompt)
            self.db.commit()
            self.db.refresh(prompt)
            return PromptRead.from_orm(prompt)
        return None
