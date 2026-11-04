"""Test: agent retrieves classification data for a product."""
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
def mock_classification_tool():
    ArgsModel = create_model("get_clfn_args", product=(str, ...))
    mock_response = json.dumps({
        "Product": "PUMP-001",
        "ProductGroup": "PUMP",
        "MaterialGroup": "001",
        "ProductHierarchy": "00000100",
    })
    async def _run(**kwargs):
        return mock_response
    return StructuredTool(
        name="get_a_clfnproduct_for_api_clfn_product_srv",
        description="Retrieve classification data for a specific product",
        args_schema=ArgsModel,
        coroutine=_run,
    )


@pytest.mark.asyncio
async def test_agent_retrieves_classification(add_agent_to_path, mock_classification_tool):
    """Agent should return product classification info including material group."""
    from agent import SampleAgent
    agent = SampleAgent()

    mock_llm_response = MagicMock()
    mock_llm_response.content = (
        "Product PUMP-001 classification:\n"
        "- Product Group: PUMP\n"
        "- Material Group: 001\n"
        "- Product Hierarchy: 00000100"
    )

    with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = {"messages": [mock_llm_response]}
        result = await agent.invoke(
            "What material group does product PUMP-001 belong to?",
            context_id="test-003",
            tools=[mock_classification_tool],
        )

    assert result.status == "completed"
    assert "PUMP" in result.message or "001" in result.message
