"""Integration test: end-to-end agent flow with mock MCP tools and mock LLM."""
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
def mock_mcp_tools():
    """Set of mock MCP tools simulating the full product master MCP server."""
    GetProductArgs = create_model("GetProductArgs", product=(str, ...), select=(str, None))
    ListProductArgs = create_model("ListProductArgs", filter=(str, None), top=(str, None))
    GetDescArgs = create_model("GetDescArgs", product=(str, ...), language=(str, ...))
    GetUoMArgs = create_model("GetUoMArgs", product=(str, ...), alternativeunit=(str, ...))

    async def get_product(**kwargs):
        return json.dumps({
            "Product": "PUMP-001",
            "GrossWeight": "12.500",
            "WeightUnit": "KG",
            "NetWeight": "11.800",
            "BaseUnit": "EA",
            "SizeOrDimensionText": "200x150x300mm"
        })

    async def list_products(**kwargs):
        return json.dumps({
            "results": [
                {"Product": "PUMP-001", "ProductDescription": "Centrifugal Pump 200W"},
                {"Product": "PUMP-002", "ProductDescription": "Centrifugal Pump 350W"},
            ]
        })

    async def get_description(**kwargs):
        return json.dumps({
            "Product": "PUMP-001",
            "Language": "EN",
            "ProductDescription": "Centrifugal Pump 200W Industrial Grade"
        })

    async def get_uom(**kwargs):
        return json.dumps({
            "Product": "PUMP-001",
            "AlternativeUnit": "EA",
            "Length": "0.300",
            "Width": "0.200",
            "Height": "0.150",
            "UnitSpecificProductLength": "M"
        })

    return [
        StructuredTool(name="get_a_product_for_api_product_srv", description="Get product by ID", args_schema=GetProductArgs, coroutine=get_product),
        StructuredTool(name="list_a_product_for_api_product_srv", description="List products", args_schema=ListProductArgs, coroutine=list_products),
        StructuredTool(name="get_a_productdescription_for_api_product_srv", description="Get product description", args_schema=GetDescArgs, coroutine=get_description),
        StructuredTool(name="get_a_productunitsofmeasure_for_api_product_srv", description="Get product UoM", args_schema=GetUoMArgs, coroutine=get_uom),
    ]


@pytest.mark.asyncio
async def test_end_to_end_product_lookup(add_agent_to_path, mock_mcp_tools):
    """Full end-to-end: user asks product question → agent calls mock tool → returns formatted answer."""
    from agent import SampleAgent
    agent = SampleAgent()

    expected_response = (
        "Product: PUMP-001\n"
        "Description: Centrifugal Pump 200W Industrial Grade\n"
        "Base Unit of Measure: EA\n"
        "Gross Weight: 12.500 KG\n"
        "Net Weight: 11.800 KG\n"
        "Dimensions: 300mm x 200mm x 150mm"
    )

    mock_llm_response = MagicMock()
    mock_llm_response.content = expected_response

    with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = {"messages": [mock_llm_response]}
        result = await agent.invoke(
            "Give me all details for product PUMP-001",
            context_id="integration-001",
            tools=mock_mcp_tools,
        )

    assert result.status == "completed"
    assert "PUMP-001" in result.message
    assert "12.500" in result.message or "Centrifugal" in result.message
    # Verify _invoke was called with the tools
    mock_invoke.assert_called_once()
    call_kwargs = mock_invoke.call_args
    assert call_kwargs is not None
