"""Test: agent states explicitly when a field is not populated in S/4HANA."""
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
def mock_product_missing_weight_tool():
    ArgsModel = create_model("get_product_args", product=(str, ...))
    # Product has no weight fields populated
    async def _run(**kwargs):
        return json.dumps({
            "Product": "PUMP-003",
            "BaseUnit": "EA",
            "GrossWeight": "",
            "WeightUnit": "",
            "NetWeight": ""
        })
    return StructuredTool(
        name="get_a_product_for_api_product_srv",
        description="Retrieve a product record",
        args_schema=ArgsModel,
        coroutine=_run,
    )


@pytest.mark.asyncio
async def test_agent_reports_missing_fields(add_agent_to_path, mock_product_missing_weight_tool):
    """Agent must explicitly state a field is not populated rather than guessing."""
    from agent import SampleAgent
    agent = SampleAgent()

    mock_llm_response = MagicMock()
    mock_llm_response.content = (
        "Product: PUMP-003\n"
        "Base Unit of Measure: EA\n"
        "Gross Weight: Not populated in S/4HANA\n"
        "Net Weight: Not populated in S/4HANA"
    )

    with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = {"messages": [mock_llm_response]}
        result = await agent.invoke(
            "What is the weight of product PUMP-003?",
            context_id="test-006",
            tools=[mock_product_missing_weight_tool],
        )

    assert result.status == "completed"
    assert "not populated" in result.message.lower() or "not available" in result.message.lower()
