from mcp import MCPError
from mcp.server import Server, ServerRequestContext
from mcp.types import (
    INVALID_PARAMS,
    CallToolRequestParams,
    CallToolResult,
    ListToolsResult,
    PaginatedRequestParams,
    TextContent,
    Tool,
)

SEARCH_BOOKS = Tool(
    name="search_books",
    description="Search the catalog by title or author.",
    input_schema={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
)


async def list_tools(ctx: ServerRequestContext, params: PaginatedRequestParams | None) -> ListToolsResult:
    return ListToolsResult(tools=[SEARCH_BOOKS])


async def call_tool(ctx: ServerRequestContext, params: CallToolRequestParams) -> CallToolResult:
    if params.name != "search_books":
        raise MCPError(INVALID_PARAMS, f"Unknown tool: {params.name}")
    args = params.arguments or {}
    text = f"Found 3 books matching {args['query']!r}."
    return CallToolResult(content=[TextContent(type="text", text=text)])
