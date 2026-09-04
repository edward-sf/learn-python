# First steps

The [landing page](https://py.sdk.modelcontextprotocol.io/) moves fast: write a server, run it, call a tool.

This page takes it slowly, with all three things a server can expose, and a name for everything along the way.

## Host, client, and server

Three words you'll see on every page from here on:

- A **host** is the LLM application: Claude, an IDE, an agent runtime. It's the thing the user is talking to.
- A **client** lives inside the host and speaks MCP. The host runs one client per server it's connected to.
- A **server** is what you build with this SDK. It exposes things to clients. It never talks to the model directly.

You write the server. Hosts are someone else's product. The SDK also gives you a `Client`. You'll use it to test your servers, and it shows up later on this page.

## The three primitives

A server exposes exactly three kinds of thing. What separates them is **who decides to use them**:

| Primitive | Controlled by | What it is | Example |
| --------- | ------------- | ---------- | ------- |
| Tools | The model | A function the model calls to take an action | An API call, a database write |
| Resources | The application | Data the host loads into the model's context | A file's contents, an API response |
| Prompts | The user | A reusable message template the user invokes by name | A slash command, a menu entry |

"Controlled by" is the whole point of the split. A tool runs because the **model** decided to call it. A resource is attached because the **application** decided the model needed it. A prompt runs because the **user** picked it.

> :information_source: Info
> If you've built a web API you already have most of the intuition: a **resource** is a `GET` (it loads data and changes nothing) and a **tool** is a `POST` (it does work and may have side effects). A **prompt** has no HTTP analogue; it's closer to a saved query the user runs by name.

## One server, all three

**server.py**
```
from mcp.server import MCPServer

mcp = MCPServer("Demo")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


@mcp.prompt()
def summarize(text: str) -> str:
    """Summarize a piece of text in one sentence."""
    return f"Summarize the following text in one sentence:\n\n{text}"
```

Three plain functions, three decorators. Each decorator is the entire registration:

- `@mcp.tool()` makes `add` a **tool**.
- `@mcp.resource("greeting://{name})` makes `greeting` a **resource template**: the `{name}` in the URI is the function's parameter.
- `@mcp.prompt()` makes `summarize` a **prompt**. The string it returns becomes a user message.

Everything else (the name, the description, the argument schema) the SDK reads from the function itself: its name, its docstring, its type hints. You never declared any of it separately.

> :fire: Tip
> The two halves of the SDK have two import paths: `from mcp import Client` and `from mcp.server import MCPServer`. There is no `from mcp import MCPServer`.

## Try it

Run it with the MCP Inspector:

```
uv run mcp dev server.py
```

Open the URL it prints. The Inspector has one tabe per primitive; walk through them in order.

**Tools**. One entry: `add`, described as *Add two numbers*. The form has required integer field for `a` and another for `b`. Fill them in, call it, and the result is `3`. The Inspector built that form from `a: int, b: int`. So does every other client.

**Resources**. The *Resources* list is empty. `greeting` is under **Resource Templates**, because `greeting://{name}` has a parameter: there is no single resource to list until someone supplies a `name`. Give it `World` and read it:

```
Hello, world!
```

**Prompts**. One entry: `summarize`, with a single required `text` argument. Get it with some text and you receive one message with `role: user` and your rendered string as the content. That's all a prompt is: a function that builds messages.

The Inspector ran your server your **stdio**, one of the transports an MCP server can speak. You don't pick one yet; [Running your server](https://py.sdk.modelcontextprotocol.io/run/) is the page for that.

## Capabilities

You saw three tabs in the Inspector. How did it know there were three?

When a client connects, the server declares its **capabilities**: which families of requests it will answer. The client uses that declaration to decide what to even ask for. You never wrote it; `MCPServer` declares it for you.

Look at it yourself. The SDK's `Client` accepts the server object directly and connects to it **in memory** (no subprocess, no port):

```
import asyncio

from mcp import Client

from server import mcp


async def main() -> None:
    async with Client(mcp) as client:
        print(client.server_capabilities.model_dump(exclude_none=True))


asyncio.run(main())
```

```
{'prompts': {'list_changed': True}, 'resources': {'subscribe': True, 'list_changed': True}, 'tools': {'list_changed': True}}
```

That dictionary is your server's declared **capabilities**. It's the first thing every connecting client learns:

| Capability | The client may now call |
| ---------- | ----------------------- |
| `tools` | `tools/list`, `tools/call` |
| `resources` | `resources/list`, `resources/templates/list`, `resources/read` |
| `prompts` | `prompts/list`, `prompts/get` |

`MCPServer` serves all three primitives, so all three are always declared.

Notice what isn't there. `completions` (argument autocomplete for resource templates and prompts) needs a handler you write, this server doesn't have one, so the capability is absent and a well-behaved client won't ask. That's the rule for everything optional: register the thing and the capability appears; [Completions](https://py.sdk.modelcontextprotocol.io/servers/completions/) prove it.