from dataclasses import Field
import uuid
from pydantic import BaseModel


from typing import Any, List, Dict, Optional, Type, Union


from ..knowledge_base.knowledge_base import KnowledgeBase
from ..tasks.tasks import Task

from ..latest_beacon_client import latest_beacon_client

def register_tools(client, tools):
    """Register tools with the client."""
    if tools is not None:
        for tool in tools:
            # Handle special tool classes from beacon.client.tools
            if tool.__module__ == 'beacon.client.tools':

                client.tool()(tool)
                continue
                
            # If tool is a class (not an instance)
            if isinstance(tool, type):
                if hasattr(tool, 'command') and hasattr(tool, 'args'):

                    client.mcp()(tool)
                else:

                    client.tool()(tool)
            else:
                # Get all attributes of the tool instance/object
                tool_attrs = dir(tool)
                
                # Filter out special methods and get only callable attributes
                functions = [attr for attr in tool_attrs 
                           if not attr.startswith('__') and callable(getattr(tool, attr))]
                
                if functions:
                    # If the tool has functions, use the tool() decorator
                    print("INSTANCE TOOL REGISTERED:", tool.__class__.__name__)

                    if not isinstance(tool, object):
                        client.tool()(tool.__class__)
                    else:
                        client.tool()(tool)
                else:
                    # If the tool has no functions, use mcp()
                    print("INSTANCE MCP REGISTERED:", tool.__class__.__name__)
                    client.mcp()(tool.__class__)
    return client


def get_or_create_client():
    """Get existing client or create a new one."""
    
    global latest_beacon_client
    
    if latest_beacon_client is not None:
        # Check if the existing client's status is False
        if not latest_beacon_client.status():
            from ..base import beaconClient
            new_client = beaconClient("localserver")
            latest_beacon_client = new_client
        return latest_beacon_client
    
    from ..base import beaconClient
    the_client = beaconClient("localserver")
    latest_beacon_client = the_client
    return the_client


def execute_task(agent_config, task: Task):
    """Execute a task with the given agent configuration."""
    global latest_beacon_client
    
    # If agent has a custom client, use it
    if hasattr(agent_config, 'client') and agent_config.client is not None:
        the_client = agent_config.client
    else:
        # Get or create client using existing process
        the_client = get_or_create_client()
    
    # Register tools if needed
    the_client = register_tools(the_client, task.tools)
    
    the_client.run(agent_config, task)
    return task.response


class AgentConfiguration(BaseModel):
    agent_id_: str = None
    job_title: str
    company_url: str = None
    company_objective: str = None
    name: str = ""
    contact: str = ""
    model: str = "openai/gpt-4o"
    client: Any = None  # Add client parameter

    def __init__(self, job_title: str = None, client: Any = None, **data):
        if job_title is not None:
            data["job_title"] = job_title
        if client is not None:
            data["client"] = client
        super().__init__(**data)

    sub_task: bool = True
    reflection: bool = True
    memory: bool = False
    caching: bool = True
    cache_expiry: int = 60 * 60
    knowledge_base: KnowledgeBase = None
    tools: List[Any] = []
    context_compress: bool = True

    @property
    def retries(self):
        if self.reflection:
            return 5
        else:
            return 2

    @property
    def agent_id(self):
        if self.agent_id_ is None:
            self.agent_id_ = str(uuid.uuid4())
        return self.agent_id_
    
    def do(self, task: Task):
        return execute_task(self, task)
    
    def print_do(self, task: Task):
        result = self.do(task)
        print(result)
        return result
