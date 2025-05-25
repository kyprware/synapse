import logging
import requests
from typing import Callable, Optional, List, Tuple

from ..models.agent_model import  AgentModel
from ..schemas.wake_schema import WakeResponseSchema
from ..schemas.agent_schema import AgentSchema, AgentUpdateSchema


logger = logging.getLogger(__name__)

def create_agent(agent_data: AgentSchema) -> Optional[AgentModel]:
    try:
        agent = AgentModel(**agent_data.model_dump())
        logger.info(f"[CREATE] Agent {agent.pk} created successfully:")
        agent.save()
        return agent
    except Exception as error:
        logger.error(f"[CREATE] Failed to create agent with UUID '{agent_data.uuid}': {error}")
        return None


def get_agent(agent_id: str) -> Optional[AgentModel]:
    try:
        return AgentModel.get(agent_id)
    except Exception as error:
        logger.error(f"[GET] Failed to fetch agent with ID '{agent_id}': {error}")
        return None


def get_agents(
    filter_fn: Callable[[AgentModel], bool] = lambda agent: True,
    sort_fn: Callable[[AgentModel], any] = lambda agent: agent.pk
) -> List[AgentModel]:
    try:
        agents = [AgentModel.get(pk) for pk in AgentModel.all_pks()]
        agents = sorted(filter(filter_fn, agents), key=sort_fn)
        logger.info(f"[GET] Retrieved {len(agents)} agents")
        return sorted(filter(filter_fn, agents), key=sort_fn)
    except Exception as error:
        logger.error(f"[GET] Failed to retrieve agent list: {error}")
        return []


def update_agent(agent_id: str, update_data: AgentUpdateSchema) -> Tuple[bool, Optional[AgentModel]]:
    try:
        updated = False
        agent = AgentModel.get(agent_id)

        for field, value in update_data.dict(exclude_unset=True).items():
            if hasattr(agent, field):
                setattr(agent, field, value)
                updated = True

        if updated:
            agent.save()
            logger.info(f"[UPDATE] Agent '{agent_id}' updated successfully")

        return True, agent
    except Exception as error:
        logger.error(f"[UPDATE] Failed to update agent '{agent_id}': {error}")
        return False, None


def delete_agent(agent_id: str) -> bool:
    try:
        AgentModel.delete(agent_id)
        logger.info(f"[DELETE] Agent '{agent_id}' deleted successfully")
        return True
    except Exception as error:
        logger.error(f"[DELETE] Failed to delete agent : {error}")
        return False


def send_wake_ping(agent_ids: List[str]) -> List[WakeResponseSchema]:
    responses: List[WakeResponseSchema] = []

    for agent_id in agent_ids:
        try:
            agent = AgentModel.get(agent_id)
            api_key = agent.decrypted_api_key
            url = getattr(agent, "ping_url", None)

            if not url:
                raise ValueError(f"Agent '{agent_id}' missing ping_url")

            response = requests.get(url, headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }, timeout=5)

            status_code = response.status_code
            success = 200 <= status_code < 300

            responses.append(WakeResponseSchema(
                agent_id=agent_id,
                url=url,
                status_code=status_code,
                success=success,
                error=(None if success else response.text),
            ))

            logger.info(f"[WAKE] Agent '{agent_id}' wake request sent to {url} - Status {response.status_code}")
        except Exception as error:
            logger.error(f"[WAKE] Failed to wake agent '{agent_id}': {error}")
            responses.append(WakeResponseSchema(
                agent_id=agent_id,
                success=False,
                error=str(error),
            ))

    return responses
