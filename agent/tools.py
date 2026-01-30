from typing import Optional, Literal, List
from pydantic import BaseModel, Field


class AgentAction(BaseModel):
    title: Literal["click", "type", "go_to", "wait_user", "ask_user", "stop"] = Field(
        ..., description="The action to perform"
    )
    target: Optional[str] = Field(
        None,
        description="The element identifier to interact with (for click/type). You must give exactly the data-ai-id attribute value",
    )
    value: Optional[str] = Field(None, description="The text to type (for type)")
    url: Optional[str] = Field(None, description="The URL to navigate to (for go_to)")
    question: Optional[str] = Field(
        None, description="The question to ask the user (for ask_user)"
    )
    reason: Optional[str] = Field(
        None,
        description="The reason for stopping (for stop) or waiting (for wait_user)",
    )


class AgentResponse(BaseModel):
    actions: List[AgentAction] = Field(
        ..., description="List of actions to perform sequentially in one turn"
    )


SYSTEM_ROLE = """
You are a deterministic web agent. You can perform actions on a web page.

Your workflow:
1. Receive a user request.
2. Analyze the 'Current UI' state.
3. Respond with a JSON object containing a list of actions.

CRITICAL RULES:
1. BATCHING: You can provide multiple actions in one turn (e.g., filling multiple fields). 
2. NAVIGATION: If you use 'go_to', it MUST be the LAST action in your turn.
3. ID PERSISTENCE: After any action that might change the page (navigation, submitting a form).
4. SEARCH FIELDS: Type your search, and if you need to select from a dropdown, use 'wait_user' as the next action so the user can see the results.
5. REPETITION: If an action (click or type) does not seem to change the page state in the next snapshot, DO NOT repeat it more than twice. Instead, use 'wait_user' to ask for help or 'ask_user' to clarify.
6. STUCK PROCESS: If you see the same UI snapshot multiple times despite your actions, assume you are stuck and use 'wait_user'.
7. Respond with JSON ONLY.
"""
