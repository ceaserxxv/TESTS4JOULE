"""Test: agent returns 'not found' message for non-existent material number (no hallucination)."""
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
def mock_empty_product_tool():
    ArgsModel = create_model("get_product_args", product=(str, ...))
    async def _run(**kwargs):
        return json.dumps({"results": []})
    return StructuredTool(
        name="get_a_product_for_api_product_srv",
        description="Retrieve a product record by material number",
        args_schema=ArgsModel,
        coroutine=_run,
    )


@pytest.mark.asyncio
async def test_agent_returns_not_found_for_unknown_product(add_agent_to_path, mock_empty_product_tool):
    """Agent must not fabricate product data when no product is found."""
    from agent import SampleAgent
    agent = SampleAgent()

    mock_llm_response = MagicMock()
    mock_llm_response.content = "No product matching NONEXISTENT-9999 was found in SAP S/4HANA."

    with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = {"messages": [mock_llm_response]}
        result = await agent.invoke(
            "What is the description of product NONEXISTENT-9999?",
            context_id="test-005",
            tools=[mock_empty_product_tool],
        )

    assert result.status == "completed"
    assert "not found" in result.message.lower() or "no product" in result.message.lower()
    # Must not contain fabricated product data
    assert "description" not in result.message.lower() or "not found" in result.message.lower()
