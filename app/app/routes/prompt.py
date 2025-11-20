# app/api/routes/prompt.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.domain.models.prompt import PromptRead
from app.domain.services.prompt import PromptService

router = APIRouter()

@router.post("/create", response_model=PromptRead)
async def create_prompt(id: str, editable_part: str, fixed_part: str, service: PromptService = Depends()):
    return await service.create_prompt(id, editable_part, fixed_part)

@router.get("/{prompt_id}", response_model=PromptRead)
async def get_prompt(prompt_id: str, service: PromptService = Depends()):
    prompt = await service.get_prompt(prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt

@router.get("/get/all", response_model=List[PromptRead])
async def list_prompts(service: PromptService = Depends()):
    return await service.list_prompts()

@router.put("/update/{prompt_id}", response_model=PromptRead)
async def update_prompt(prompt_id: str, editable_part: Optional[str] = None, fixed_part: Optional[str] = None, service: PromptService = Depends()):
    prompt = await service.update_prompt(prompt_id, editable_part, fixed_part)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt
