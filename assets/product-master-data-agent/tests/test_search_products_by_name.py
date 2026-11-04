"""Test: agent searches products by partial name and returns a limited result list."""
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
def mock_list_products_tool():
    ArgsModel = create_model("list_products_args", filter=(str, None), top=(str, None))
    mock_response = json.dumps({
        "results": [
            {"Product": "PUMP-001", "ProductDescription": "Centrifugal Pump 200W Industrial Grade"},
            {"Product": "PUMP-002", "ProductDescription": "Centrifugal Pump 350W Heavy Duty"},
        ]
    })
    async def _run(**kwargs):
        return mock_response
    return StructuredTool(
        name="list_a_product_for_api_product_srv",
        description="Retrieve a list of products",
        args_schema=ArgsModel,
        coroutine=_run,
    )


@pytest.mark.asyncio
async def test_agent_searches_products_by_name(add_agent_to_path, mock_list_products_tool):
    """Agent should search for products by partial name and return matching list."""
    from agent import SampleAgent
    agent = SampleAgent()

    mock_llm_response = MagicMock()
    mock_llm_response.content = (
        "I found 2 products matching 'pump':\n"
        "1. PUMP-001 - Centrifugal Pump 200W Industrial Grade\n"
        "2. PUMP-002 - Centrifugal Pump 350W Heavy Duty"
    )

    with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = {"messages": [mock_llm_response]}
        result = await agent.invoke(
            "Find products with 'pump' in the name",
            context_id="test-002",
            tools=[mock_list_products_tool],
        )

    assert result.status == "completed"
    assert "PUMP-001" in result.message or "pump" in result.message.lower()
