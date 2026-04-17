"""
SuppieAgent — a conversational LangChain agent registered with Gale Broker.

Selects the LLM based on the HYPERSCALER environment variable:
  - aws  → AWS Bedrock (Claude)
  - gcp  → Google Gemini (via Vertex AI)
"""

import os
import uuid
from typing import Optional

from langchain.agents import create_agent
from langchain_aws import ChatBedrock
from langchain_google_genai import ChatGoogleGenerativeAI

from totoms.evt.TotoMessageBus import TotoMessageBus
from totoms.gale.agent.GaleConversationalAgent import GaleConversationalAgent
from totoms.gale.model.AgentConversationMessage import AgentConversationMessage, StreamInfo
from totoms.gale.model.AgentManifest import AgentManifest
from totoms.model.TotoConfig import TotoControllerConfig
from totoms.TotoLogger import TotoLogger

from agent.tools import add_item_to_list, get_common_items


SYSTEM_PROMPT = """
    You are an agent that helps the user manage their shopping list (supermarket list).

    Important rules to follow:
    1.  When a user wants to add items to the shopping list, double check with the list of most common items used by the user.
        If some terms in the items that the user wants to add are mispelled or look weird, double check the common items list and pick the one that has the highest potential of fitting what the user meant (e.g. closest matching).

    2.  Always avoid adding multiple times an item to the shopping list. Make sure that you are not creating duplicates before adding items to the shopping list.
"""

TOOLS = [add_item_to_list, get_common_items]


def _create_llm(hyperscaler: str):
    """Create the appropriate LLM based on the hyperscaler."""
    provider = hyperscaler.lower()

    if provider == "gcp":
        project = os.environ.get("GCP_PID")
        location = os.environ.get("GCP_REGION", "europe-west1")
        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

        return ChatGoogleGenerativeAI(
            model=model,
            project=project,
            location=location,
            temperature=0,
            thinking_budget=-1,
            include_thoughts=True,
        )

    if provider == "aws":
        model_id = os.environ.get("BEDROCK_MODEL_ID", "eu.anthropic.claude-sonnet-4-5-20250929-v1:0")
        aws_region = os.environ.get("AWS_REGION", "eu-north-1")

        return ChatBedrock(
            model_id=model_id,
            region_name=aws_region,
            model_kwargs={
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": 4096,
                },
            },
        )

    raise ValueError(f"Unsupported HYPERSCALER '{hyperscaler}'. Use 'aws' or 'gcp'.")


class SuppieAgent(GaleConversationalAgent):
    """Conversational shopping-list agent backed by a LangChain LLM."""

    def __init__(self, message_bus: Optional[TotoMessageBus], config: TotoControllerConfig):
        super().__init__(message_bus, config)
        hyperscaler = os.environ.get("HYPERSCALER", "aws").lower()
        llm = _create_llm(hyperscaler)
        self._agent = create_agent(llm, TOOLS, system_prompt=SYSTEM_PROMPT)

    def get_manifest(self) -> AgentManifest:
        return AgentManifest(
            agent_type="conversational",
            agent_id="suppie",
            human_friendly_name="Suppie",
            description="Shopping-list assistant that helps you manage your supermarket list.",
        )

    async def on_message(self, message: AgentConversationMessage) -> AgentConversationMessage:
        
        logger = TotoLogger.get_instance()
        
        logger.log(message.conversation_id, f"Received message for agent {message.agent_id}: {message.message}")
        
        stream_id = str(uuid.uuid4())

        # Acknowledge receipt while the LLM processes
        await self.publish_message(AgentConversationMessage(
            conversation_id=message.conversation_id,
            message_id=str(uuid.uuid4()),
            agent_id=message.agent_id,
            message="Got your message, working on it!",
            actor="agent",
            stream=StreamInfo(stream_id=stream_id, sequence_number=1, last=False),
        ))

        result = self._agent.invoke({"messages": [("human", message.message)]})
        answer = result["messages"][-1].content
        
        logger.log(message.conversation_id, f"LLM response for agent {message.agent_id}: {answer}")

        # Return the final response
        return AgentConversationMessage(
            conversation_id=message.conversation_id,
            message_id=message.message_id,
            agent_id=message.agent_id,
            message=answer,
            actor="agent",
            stream=StreamInfo(stream_id=stream_id, sequence_number=2, last=True),
        )
