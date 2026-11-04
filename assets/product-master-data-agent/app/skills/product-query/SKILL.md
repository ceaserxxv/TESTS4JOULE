---
name: product-query
description: Guides the agent on how to query product master data from SAP S/4HANA, handle ambiguous queries, format responses, and apply guardrails for data accuracy
---

# Product Query Skill

## When to Use This Skill

Load this skill when the user asks any question about a product, material, or item — including its name, description, unit of measure, weight, dimensions, or classification.

## Query Handling Rules

### Case 1: User provides a material number (e.g., "product 1234", "material P-001")

1. Call the product retrieval tool directly with the material number as the filter.
2. Return all available standard fields: product ID, description, base unit of measure, gross weight, net weight, and dimensions (width, length, height with their units).
3. If a field is not returned by the API, explicitly state: "The [field name] is not populated in S/4HANA for this product."

### Case 2: User provides a product name or partial name (e.g., "find products with pump in the name")

1. Call the product search tool with the name or partial name as the filter.
2. Return up to 10 results as a numbered list showing: material number, product description.
3. If more than 10 results are returned by the API, show only the first 10 and tell the user: "More than 10 products match your search. Please refine your query with a more specific name or a material number."
4. If the user then selects one, retrieve its full details using the material number.

### Case 3: User query is ambiguous (no product identifier or name given)

1. Ask exactly ONE clarifying question, choosing the most relevant:
   - "Could you provide the material number or product name you are looking for?"
2. Do NOT call any tool before receiving the user's answer.
3. Once the user provides the identifier, proceed with Case 1 or Case 2.

## Response Formatting

Always format product detail responses as a structured list:

```
Product: [Product ID]
Description: [Description] (or "Not populated in S/4HANA")
Base Unit of Measure: [UoM] (or "Not populated in S/4HANA")
Gross Weight: [value] [unit] (or "Not populated in S/4HANA")
Net Weight: [value] [unit] (or "Not populated in S/4HANA")
Dimensions: [width] x [length] x [height] [unit] (or "Not populated in S/4HANA")
```

## Guardrails

- **Never fabricate product data.** Every field value must come directly from the API response.
- **Never infer or estimate** a field value based on other fields (e.g., do not derive weight from dimensions).
- **If the product does not exist**, respond: "No product matching [query] was found in SAP S/4HANA."
- **If the API returns an error**, relay the exact error message to the user without adding suggestions.
- **Out of scope topics**: If the user asks about pricing, stock levels, inventory replenishment, or product creation/modification, respond: "I can only help with product master data such as descriptions, units of measure, and dimensions. For [topic], please use the appropriate S/4HANA application."

## Examples

**User:** "What is the description of product 1234?"
**Action:** Call product retrieval tool with material number "1234", return the Description field.

**User:** "Find all products with 'valve' in the name."
**Action:** Call product search tool with name filter "valve", return up to 10 results.

**User:** "Tell me about the product."
**Action:** Ask: "Could you provide the material number or product name you are looking for?"
