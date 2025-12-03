from uuid import uuid4
from fastapi import APIRouter
from services.ppt import process_data_to_ppt,call_llm
from schemas.response import Message
# Router Initialization
router = APIRouter()

@router.post("/render")
async def generate_ppt(data:dict):
    request_id=str(uuid4())
    return await process_data_to_ppt(request_id,data)



@router.post("/generate")
async def generate_ai_json(message:Message):
    ppt_json = call_llm(message.message)
    return {"data":ppt_json}