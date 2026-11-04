"""Test: agent retrieves and formats product details for a known material number."""
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
    if p in sys.path:
        sys.path.remove(p)


@pytest.fixture
def mock_product_tool():
    """Mock MCP tool returning a product record."""
    ArgsModel = create_model("get_a_product_args", product=(str, ...), select=(str, None))
    mock_response = json.dumps({
        "Product": "PUMP-001",
        "GrossWeight": "12.500",
        "WeightUnit": "KG",
        "NetWeight": "11.800",
        "BaseUnit": "EA",
        "SizeOrDimensionText": "200x150x300mm"
    })
    async def _run(**kwargs):
        return mock_response
    return StructuredTool(
        name="get_a_product_for_api_product_srv",
        description="Retrieve a single product record by material number",
        args_schema=ArgsModel,
        coroutine=_run,
    )


@pytest.mark.asyncio
async def test_agent_retrieves_product_by_material_number(add_agent_to_path, mock_product_tool):
    """Agent should return product details when given a valid material number."""
    from agent import SampleAgent

    agent = SampleAgent()

    mock_llm_response = MagicMock()
    mock_llm_response.content = (
        "Product: PUMP-001\n"
        "Gross Weight: 12.500 KG\n"
        "Net Weight: 11.800 KG\n"
        "Base Unit of Measure: EA\n"
        "Dimensions: 200x150x300mm"
    )

    with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = {"messages": [mock_llm_response]}
        result = await agent.invoke(
            "What is the weight of product PUMP-001?",
            context_id="test-001",
            tools=[mock_product_tool],
        )

    assert result.status == "completed"
    assert "PUMP-001" in result.message
    assert "12.500" in result.message or "KG" in result.message
