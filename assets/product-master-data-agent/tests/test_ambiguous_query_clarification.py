"""Test: agent asks one clarifying question when no product identifier is given."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.fixture
def add_agent_to_path(agent_app_path):
    import sys
    p = str(agent_app_path)
    if p not in sys.path:
        sys.path.insert(0, p)
    yield


@pytest.mark.asyncio
async def test_agent_asks_clarification_for_ambiguous_query(add_agent_to_path):
    """When user asks without providing a product ID or name, agent should ask for clarification."""
    from agent import SampleAgent
    agent = SampleAgent()

    mock_llm_response = MagicMock()
    mock_llm_response.content = (
        "Could you provide the material number or product name you are looking for?"
    )

    with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = {"messages": [mock_llm_response]}
        result = await agent.invoke(
            "Tell me about the product.",
            context_id="test-004",
            tools=[],
        )

    assert result.status == "completed"
    assert "material number" in result.message.lower() or "product name" in result.message.lower() or "?" in result.message
