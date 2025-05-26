from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query

from ..services import agent_service
from ..models.agent_model import  AgentModel
from ..schemas.wake_schema import WakeRequestSchema, WakeResponseSchema
from ..schemas.agent_schema import AgentCreateSchema, AgentUpdateSchema, AgentResponseSchema


router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/", response_model=AgentResponseSchema)
def create_agent(agent_data: AgentCreateSchema) -> AgentResponseSchema:
    try:
        agent = agent_service.create_agent(agent_data)
        return AgentResponseSchema(detail="Agent created successfully", data=agent)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/", response_model=AgentResponseSchema)
def list_agents(
    sort_by: Optional[str] = Query("pk", description="Field to sort by (uuid, ping_url, etc.)")
) -> AgentResponseSchema:
    def filter_fn(_: AgentModel) -> bool:
        return True

    def sort_fn(agent: AgentModel):
        key = sort_by or "pk"
        return getattr(agent, key)

    agents = agent_service.get_agents(filter_fn, sort_fn)
    return AgentResponseSchema(detail="Retrieved agents successfully", data=agents)


@router.get("/ping", response_model=List[WakeResponseSchema])
def wake_agents(request: WakeRequestSchema) -> List[WakeResponseSchema]:
    try:
        responses = agent_service.send_wake_ping(request.agent_ids)
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=AgentResponseSchema)
def get_agent(agent_id: str) -> AgentResponseSchema:
    agent = agent_service.get_agent(agent_id)

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return AgentResponseSchema(detail="Retrieved agent successfully", data=agent)


@router.put("/{agent_id}", response_model=AgentResponseSchema)
def update_agent(agent_id: str, update_data: AgentUpdateSchema) -> AgentResponseSchema:
    updated, agent = agent_service.update_agent(agent_id, update_data)

    if not updated:
        raise HTTPException(status_code=404, detail="Failed to update agent")

    return AgentResponseSchema(detail="Agent updated successfully", data=agent)


@router.delete("/{agent_id}", response_model=AgentResponseSchema)
def delete_agent(agent_id: str) -> AgentResponseSchema:
    deleted = agent_service.delete_agent(agent_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")

    return AgentResponseSchema(detail="Agent deleted successfully", data={})
