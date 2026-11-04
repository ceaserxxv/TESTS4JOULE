# Product Master Data AI Agent for Sales Representatives

SAP S/4HANA Public Cloud Edition — Natural Language Product Inquiry Agent

## Business Challenge

Sales Representatives spend too much time navigating SAP S/4HANA screens to look up basic product information. With a catalog of over 100,000 products, this results in significant delays (up to 5 minutes per query) and reduces selling efficiency. A conversational AI agent is needed to let Sales Reps ask natural language questions and receive instant, accurate answers about product master data directly within SAP S/4HANA.

## Business Goals & Success Criteria

| Metric | Baseline | Target | Timeline | Process / Capability | Source |
|--------|----------|--------|----------|----------------------|--------|
| Time to find product information | 5 minutes | < 30 seconds | — | Product Master Data Lookup (Lead to Cash) | user |

## Key Milestones

1. **Agent Connectivity** — Agent successfully authenticates and retrieves data from the SAP S/4HANA Product Master API (API_PRODUCT_SRV)
2. **Natural Language Understanding** — Agent accurately interprets Sales Rep questions about product name, description, unit of measure, weight, and dimensions
3. **Large Catalog Handling** — Agent returns relevant results from a catalog of 100,000+ products within a response time of under 5 seconds
4. **Joule Integration** — Agent is surfaced and accessible as a Joule copilot extension inside SAP S/4HANA for Sales Representatives
5. **User Acceptance** — Sales Reps can complete a product lookup task end-to-end without navigating S/4HANA screens

## Business Architecture (RBA)

### End-to-End Process

Lead to Cash Standard B2B

### Process Hierarchy

```
Lead to Cash Standard B2B (E2E)
└── Plan to Optimize Marketing and Sales (Phase)
    └── Plan prices and promotions (BPS-359_002)
        └── Plan and define sales prices
        └── Access and query product master data for sales context
```

### Summary

Sales Representatives querying product master data to support their sales activities maps to the Lead to Cash Standard B2B process, specifically within the Plan to Optimize Marketing and Sales phase. The agent accelerates access to product master data needed during customer interactions and sales planning.

## Fit Gap Analysis

| Requirement (business) | Standard asset(s) found | API ORD ID | MCP Server ORD ID | MCP Server Version | Webhook API ORD ID | Data Product ORD ID | Gap? | Notes / assumptions |
|---|---|---|---|---|---|---|---|---|
| Query basic product details (name, description, UoM, weight, dimensions) | SAP S/4HANA Cloud Public Edition — Sales Price Planning and Definition | `sap.s4:apiResource:API_PRODUCT_SRV:v1` | — | — | — | — | No | Product Master (A2X) API is available; custom MCP translation file required |
| Query product classification and characteristics | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1` | — | — | — | — | No | Product Master with Classification API is available |
| Query product availability / stock levels | SAP S/4HANA Cloud Public Edition | `sap.s4:apiResource:CE_API_PRODUCT_AVAILY_INFO_0001:v1` | — | — | — | — | No | Product Availability Info (CE) API is available |
| Natural language interface for product queries | — | — | — | — | — | — | Yes | No pre-built NL agent exists; custom Python AI agent required |
| Joule copilot integration / embedding | — | — | — | — | — | — | Yes | Agent must follow A2A protocol for Joule extension compatibility |

### Key Findings

- The SAP S/4HANA Public Cloud Edition exposes three relevant product APIs (Product Master, Classification, Availability) that cover the core data needs.
- No pre-built MCP servers exist for these APIs; custom MCP translation files must be generated from the EDMX/OpenAPI specifications.
- Unavailable APIs in this landscape include Product Specification, Pricing, and OP (on-premise) variants — these are excluded from scope.
- A custom Python AI agent (A2A protocol) is required to provide natural language understanding over product master data.
- Initial scope is limited to basic product details (name, description, UoM, weight, dimensions) based on user confirmation.
- The agent must handle a very large product catalog (100,000+ products), requiring efficient query and filtering strategies via the API.

## Recommendations

### AI Agent for Natural Language Product Master Data Queries

#### Executive Summary

Python AI agent with MCP tools over S/4HANA Product Master API, embedded in Joule.

#### Recommended Solution

Build a pro-code Python AI agent (A2A protocol) that connects to the SAP S/4HANA Public Cloud Product Master API via custom MCP tools. The agent interprets natural language questions from Sales Representatives, calls the appropriate API endpoints, and returns structured, human-readable answers. The agent is deployed as a Joule copilot extension, making it accessible directly within the SAP S/4HANA interface.

Key components:
- Python AI agent using the A2A protocol (Joule Studio runtime)
- Custom MCP translation file for `API_PRODUCT_SRV:v1` (Product Master)
- Optional: MCP tools for `API_CLFN_PRODUCT_SRV:v1` (Classification) for richer answers
- Joule extension descriptor for embedding in SAP S/4HANA

#### Problem Statement

Sales Representatives must navigate multiple screens in SAP S/4HANA to find basic product details, wasting up to 5 minutes per lookup. With 100,000+ products in the catalog, this is a significant drag on sales productivity.

#### Affected User Roles

- Sales Representative (primary)
- Sales Manager (secondary — may benefit from same capability)

#### Important Factors

##### Reduces manual navigation through conversational access

Sales Reps can ask "What is the weight of product X?" or "Give me the description for material 1234" and get an instant answer without navigating transaction screens.

##### Large catalog requires precise API filtering

With 100,000+ products, the agent must pass specific search criteria (material number, product name) to the API rather than fetching all results. The design must avoid over-broad queries.

##### MCP tool generation is a prerequisite

No pre-built MCP servers exist for the product APIs. Generating and validating MCP translation files from the OData specs is a required first step in implementation.

#### Potential Risks

##### API field coverage may not fully match user expectations

The Product Master API covers standard fields. Highly custom or extension fields may not be exposed via the standard API and could require additional configuration.

##### Response quality depends on product data completeness in S/4HANA

If product master records are incomplete (missing descriptions, weights), the agent will return incomplete data. This is a data quality issue, not an agent issue.

#### Recommended Solution Category

AI Agent

#### Intent Fit

92%
