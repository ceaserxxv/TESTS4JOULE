"""Test: agent retains product context across a two-turn conversation."""
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from langchain_core.tools import StructuredTool
from pydantic import create_model


@pytest.fixture
def add_agent_to_path(agent_app_path):
    import sys
    p = str(agent_app_path)
    if p not in sys.path:
        sys.path.insert(0, p)
    yield


@pytest.fixture
def mock_product_tool():
    ArgsModel = create_model("get_product_args", product=(str, ...))
    async def _run(**kwargs):
        return json.dumps({
            "Product": "PUMP-001",
            "BaseUnit": "EA",
            "GrossWeight": "12.500",
            "WeightUnit": "KG"
        })
    return StructuredTool(
        name="get_a_product_for_api_product_srv",
        description="Retrieve a product record",
        args_schema=ArgsModel,
        coroutine=_run,
    )


@pytest.mark.asyncio
async def test_agent_handles_multi_turn_conversation(add_agent_to_path, mock_product_tool):
    """Agent should use context from previous turns to answer follow-up questions."""
    from agent import SampleAgent
    agent = SampleAgent()
    context_id = "test-007"

    # Turn 1: Ask for description
    turn1_response = MagicMock()
    turn1_response.content = "PUMP-001 is the Centrifugal Pump 200W Industrial Grade."

    # Turn 2: Follow-up about weight (agent should recall PUMP-001 from context)
    turn2_response = MagicMock()
    turn2_response.content = "PUMP-001 has a gross weight of 12.500 KG."

    call_count = 0
    async def mock_invoke_side_effect(**kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return {"messages": [turn1_response]}
        return {"messages": [turn2_response]}

    with patch.object(agent, "_invoke", new_callable=AsyncMock, side_effect=mock_invoke_side_effect):
        result1 = await agent.invoke("What is product PUMP-001?", context_id=context_id, tools=[mock_product_tool])
        result2 = await agent.invoke("What is its weight?", context_id=context_id, tools=[mock_product_tool])

    assert result1.status == "completed"
    assert result2.status == "completed"
    assert "12.500" in result2.message or "KG" in result2.message
