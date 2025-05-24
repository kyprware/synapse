from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/agents/hello")
def get_agent():
    return { "data": "Hello World!" }
