from anus.tools.base.tool import BaseTool
from anus.tools.base.tool_result import ToolResult

class DummyActionTool(BaseTool):
    """
    Заглушка для инструмента dummy_action, используемая в качестве fallback.
    """
    name = "dummy_action"
    description = "Заглушка для действий по умолчанию, если не найден подходящий инструмент."
    
    async def execute(self, **kwargs):
        return ToolResult(success=True, result="Fallback action executed. No operation performed.")
