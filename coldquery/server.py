from fastmcp import FastMCP, Context
import os
import importlib
import logging
import functools
import inspect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coldquery")

mcp = FastMCP("ColdQuery")

def auth_wrapper(func):
    @functools.wraps(func)
    async def wrapper(ctx: Context, *args, **kwargs):
        tool_name = func.__name__

        # Auth Check
        is_unlocked = ctx.session.get("unlocked")
        if not is_unlocked:
             raise ValueError(f"Tool '{tool_name}' is locked. Use 'auth_unlock' with valid token to enable dangerous tools.")

        # Forward call
        sig = inspect.signature(func)
        wants_ctx = False
        ctx_param_name = None

        for name, param in sig.parameters.items():
            if param.annotation == Context or name in ("ctx", "context"):
                wants_ctx = True
                ctx_param_name = name
                break

        pass_kwargs = kwargs.copy()
        if wants_ctx and ctx_param_name:
            pass_kwargs[ctx_param_name] = ctx

        return await func(*args, **pass_kwargs)
    return wrapper

# Dynamic Tool Loading
def load_tools():
    tools_path = os.path.join(os.path.dirname(__file__), "tools")
    if not os.path.exists(tools_path):
        logger.warning(f"Tools directory not found: {tools_path}")
        return

    for file in os.listdir(tools_path):
        if file.endswith(".py") and not file.startswith("__"):
            name = file[:-3]
            try:
                module = importlib.import_module(f"coldquery.tools.{name}")
                func = getattr(module, name, None)
                if func and callable(func):
                    # Apply auth wrapper to dangerous tools
                    dangerous_prefixes = ("admin_", "schema_", "query_write")
                    is_dangerous = any(name.startswith(p) for p in dangerous_prefixes)

                    if is_dangerous:
                        mcp.add_tool(auth_wrapper(func))
                        logger.info(f"Loaded tool (LOCKED): {name}")
                    else:
                        mcp.add_tool(func)
                        logger.info(f"Loaded tool: {name}")
                else:
                    logger.debug(f"No matching function found in {file}")
            except Exception as e:
                logger.error(f"Failed to load tool {name}: {e}")

load_tools()

if __name__ == "__main__":
    mcp.run()
