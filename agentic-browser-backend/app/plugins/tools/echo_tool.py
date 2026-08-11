from typing import Any, Dict
from app.tools.registry import BaseTool, ToolContext, register


class EchoTool(BaseTool):
    name = "echo"
    description = "Echo back the provided text"
    arguments = {"text": str}
    requires_confirm = False

    async def execute(self, arguments: Dict[str, Any], ctx: ToolContext, confirm: bool = False) -> Dict[str, Any]:
        return {"tool": self.name, "result": arguments.get("text", "")}


register(EchoTool())
