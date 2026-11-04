# Specification: product-master-data-agent

> **Guidelines**: Read all applicable guidelines before executing ANY tasks below:
> - [guidelines.md](../guidelines.md) — Universal execution rules
> - [guidelines-agent.md](../guidelines-agent.md) — Universal agent patterns
> - [guidelines-agent-python.md](../guidelines-agent-python.md) — Python implementation details
> - [guidelines-agent-skills.md](../guidelines-agent-skills.md) — Runtime skills patterns
> - [guidelines-agent-mcp.md](../guidelines-agent-mcp.md) — MCP integration patterns

---

## Data Dependencies

No Data Product ORD IDs. All data is sourced directly from SAP S/4HANA OData APIs via MCP tools.

- API ORD ID (primary): `sap.s4:apiResource:API_PRODUCT_SRV:v1` → spec at `specification/product-master-data-agent/api-specs/API_PRODUCT_SRV.edmx`
- API ORD ID (secondary): `sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1` → spec at `specification/product-master-data-agent/api-specs/API_CLFN_PRODUCT_SRV.edmx`

---

## MCP Tool Scope

```
MCP API: sap.s4:apiResource:API_PRODUCT_SRV:v1
MCP tool scope: read-only
Resources in scope: A_Product, A_ProductDescription, A_ProductBasicText, A_ProductSalesDelivery, A_ProductUnitsOfMeasure
```

```
MCP API: sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1
MCP tool scope: read-only
Resources in scope: A_ClfnProduct, A_ClfnProductCharc
```

---

## Basic Setup

- [x] Read `product-requirements-document.md` and `intent.md` thoroughly before starting any implementation tasks
- [x] Bootstrap agent code in `assets/product-master-data-agent/` using instructions from the `sap-agent-bootstrap` section in the agent skill (invoke from inside `assets/product-master-data-agent/`, use copy commands — do NOT create files manually)
- [x] Install dependencies, validate the agent starts and responds at `/.well-known/agent.json`

---

## Runtime Skills

- [x] Evaluate whether runtime skills are needed based on the PRD. The agent handles natural language product queries with straightforward API lookups — no complex multi-step approval workflow is required. A single runtime skill for **product query guidance** is appropriate to keep the system prompt lean.
- [x] Create `assets/product-master-data-agent/app/skills/product-query/SKILL.md` with:
  - YAML frontmatter: `name: product-query`, `description: Guides the agent on how to query product master data from SAP S/4HANA`
  - Body: Instructions for the agent on:
    - How to handle queries when the user provides a material number vs. a product name
    - How to handle ambiguous queries (ask one clarifying question — material number or partial name)
    - How to format product detail responses (structured, human-readable: field name + value pairs)
    - How to handle large result sets (return up to 10 matches; ask the user to refine if more)
    - How to handle missing data fields (explicitly state the field is not populated in S/4HANA)
    - Guardrail: Never fabricate or infer field values; only return data from the API response

---

## Project-Specific Tasks

### Agent System Prompt

- [x] Open `assets/product-master-data-agent/app/agent.py` and update the `@prompt_section` / `get_system_prompt` body with the agent's purpose and behaviour:
  - Agent identity: "You are a Product Master Data Assistant for Sales Representatives. You help users look up product information from SAP S/4HANA by answering natural language questions about product details."
  - Scope: Answer questions about product name, description, unit of measure, gross weight, net weight, and dimensions.
  - Tool usage: Use the available MCP tools to retrieve product data. Never fabricate product information.
  - Clarification rule: If the user's query is ambiguous (no product ID or name provided), ask exactly one clarifying question before calling any tool.
  - Accuracy rule: If a field is not available in the API response, tell the user the field is not populated rather than guessing.
  - Catalog size: The catalog contains 100,000+ products. Always pass specific filter criteria (material number or name search) to avoid over-broad queries.
  - Out of scope: Do not answer questions about pricing, stock levels, or product creation/modification. Politely redirect the user if they ask about these topics.

### REQ-01 & REQ-02: Natural Language Product Query and Detail Retrieval

- [x] Ensure the MCP tools from `API_PRODUCT_SRV:v1` are wired into the agent so it can:
  - Retrieve a single product record by material number (maps to `A_Product` entity)
  - Retrieve product descriptions by material number and language (maps to `A_ProductDescription`)
  - Retrieve units of measure for a product (maps to `A_ProductUnitsOfMeasure`)
- [x] Verify the agent returns the following fields when queried for a product:
  - Product/Material number
  - Product name / description
  - Base unit of measure
  - Gross weight + weight unit
  - Net weight + weight unit
  - Width, length, height + dimension unit
- [x] Test: Ask "What is the description of product <test-material-number>?" and verify the agent returns the correct description from the API.
- [x] Test: Ask "Give me the weight and dimensions for material <test-material-number>" and verify all weight/dimension fields are returned.

### REQ-03: Large Catalog Search

- [x] Ensure the MCP tool for `A_Product` supports filtering by `ProductDescription` or similar searchable field to enable partial-name searches across the catalog
- [x] Implement search result limiting in the agent system prompt / skill: return at most 10 matches per query; if more exist, prompt the user to refine the search
- [x] Test: Ask "Find products with 'pump' in the name" and verify the agent returns a filtered, manageable list (not thousands of results)
- [x] Test: Verify that a search returning more than 10 results asks the user to provide a more specific query

### REQ-04: Joule Copilot Integration

- [x] Ensure the agent is registered as a Joule extension via the `agent-extension` asset (handled by `setup-solution` skill and the agent extension descriptor)
- [x] Ensure `asset.yaml` declares the correct agent extension metadata so Joule can discover and invoke the agent
- [x] Verify that `/.well-known/agent.json` returns a valid A2A agent card with the correct name, description, and capabilities

### REQ-05: Grounded, Accurate Responses

- [x] Add a guardrail in the agent system prompt: "If no product is found for the given query, respond with a clear message that no matching product was found. Do not suggest alternative products or infer data."
- [x] Add a guardrail: "Never return information that was not present in the API tool response. If a field is missing from the response, state that it is not available."
- [x] Test: Ask about a non-existent material number and verify the agent responds with a "not found" message rather than hallucinating product data.

### REQ-06 (High-Want): Product Classification Query

- [x] Ensure MCP tools from `API_CLFN_PRODUCT_SRV:v1` are wired into the agent so it can:
  - Retrieve classification data for a product (maps to `A_ClfnProduct`)
  - Retrieve product characteristic values (maps to `A_ClfnProductCharc`)
- [x] Update the agent system prompt to include: "You can also answer questions about product classification, product hierarchy, and material group using the classification MCP tools."
- [x] Test: Ask "What material group does product <test-material-number> belong to?" and verify the correct classification data is returned.

### REQ-07 (High-Want): Conversational Follow-Up

- [x] Verify the agent framework retains conversation context across multiple turns within the same session
- [x] Test a multi-turn conversation: (1) Ask for product description → get answer; (2) Follow up with "What is its weight?" without repeating the product number → verify the agent uses the context from turn 1 to answer turn 2.

---

## Business Instrumentation

- [x] Implement structured logging and OpenTelemetry custom spans for each milestone from the PRD. Follow the pattern `[MILESTONE_ID].[achieved|missed]: [description]`. See [guidelines-agent-python.md](../guidelines-agent-python.md) for Python-specific implementation.

  | Milestone ID | Achieved condition | Log on achievement | Log on miss |
  |---|---|---|---|
  | M1 | Agent authenticated and retrieved data from `API_PRODUCT_SRV` | `M1.achieved: Agent successfully authenticated and retrieved product data from API_PRODUCT_SRV` | `M1.missed: Agent failed to connect to or authenticate with API_PRODUCT_SRV` |
  | M2 | Natural language query successfully mapped to product API call | `M2.achieved: Natural language query successfully interpreted and mapped to product API call` | `M2.missed: Query could not be interpreted or mapped to a product API call` |
  | M3 | Product search completed within target latency for large catalog | `M3.achieved: Product search completed within target latency for large catalog` | `M3.missed: Product search exceeded latency threshold or returned no results from large catalog` |
  | M4 | Agent invoked via Joule copilot extension in SAP S/4HANA | `M4.achieved: Agent successfully invoked via Joule copilot extension in SAP S/4HANA` | `M4.missed: Agent could not be invoked or did not respond via Joule copilot extension` |
  | M5 | Sales Rep completed end-to-end product lookup via agent | `M5.achieved: Sales Rep completed end-to-end product lookup via agent without S/4HANA screen navigation` | `M5.missed: Sales Rep required manual S/4HANA navigation to complete product lookup` |

- [x] Verify `bootstrap(app)` is called after `app = server.build()` in `main.py`

---

## MCP Tool Integration

- [x] During API discovery, verify `api-discovery-results.md` exists (or create it) at workspace root with ORD IDs:
  - `sap.s4:apiResource:API_PRODUCT_SRV:v1`
  - `sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1`
- [x] Invoke `mcp-translation-file` skill for `specification/product-master-data-agent/api-specs/API_PRODUCT_SRV.edmx` (ORD ID: `sap.s4:apiResource:API_PRODUCT_SRV:v1`, type: `edmx`) to generate MCP translation file and MCP server asset
- [x] Invoke `mcp-translation-file` skill for `specification/product-master-data-agent/api-specs/API_CLFN_PRODUCT_SRV.edmx` (ORD ID: `sap.s4:apiResource:API_CLFN_PRODUCT_SRV:v1`, type: `edmx`) to generate MCP translation file and MCP server asset
- [x] Invoke `setup-solution` skill to register all generated MCP server assets and the agent asset in `solution.yaml` and their respective `asset.yaml` files
- [x] Wire MCP tool loading in `agent.py` using `get_mcp_tools()` from the `mcp_tools` module — see [guidelines-agent-python.md](../guidelines-agent-python.md) for the canonical pattern. NEVER import directly from `sap_cloud_sdk.agentgateway`. NEVER create direct HTTP clients for the S/4HANA APIs.
- [x] Add MCP server dependencies to `assets/product-master-data-agent/asset.yaml` under `requires` — one entry per generated MCP server, using exact ORD IDs from the generated assets
- [x] Generate `mcp-mock.json` using the `mcp-mock-config` skill after MCP translation files are generated (required before tests can run)

---

## Testing

- [x] `conftest.py` only sets `IBD_TESTING=true` — this causes the agent to run with mock MCP tool results during tests
- [x] Write unit tests in `assets/product-master-data-agent/tests/`:
  - `test_get_product_by_material_number.py` — verify agent retrieves and formats product details for a known material number
  - `test_search_products_by_name.py` — verify agent searches by partial name and returns a limited result list
  - `test_get_product_classification.py` — verify agent retrieves classification data for a product
  - `test_ambiguous_query_clarification.py` — verify agent asks one clarifying question when no product identifier is given
  - `test_product_not_found.py` — verify agent returns a "not found" message for a non-existent material number (no hallucination)
  - `test_missing_field_handling.py` — verify agent explicitly states a field is not populated when it is absent from the API response
  - `test_multi_turn_context.py` — verify agent retains product context across a two-turn conversation
- [x] Run each test immediately after writing it; fix any failures before proceeding
- [x] Write one integration test in `assets/product-master-data-agent/tests/test_integration.py` executing the end-to-end flow: user asks a product question → agent interprets → calls mock MCP tool → returns formatted answer
- [x] Run `pytest` from `assets/product-master-data-agent/` (no args, no extra flags) — if coverage < 70%, add tests until the threshold is met
- [x] Run `pytest` again from `assets/product-master-data-agent/` (no args) to generate final `test_report.json`
- [x] Verify `test_report.json` exists in `assets/product-master-data-agent/` — if not, run pytest again until it does
