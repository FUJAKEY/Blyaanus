import logging
import os
import time
import yaml
from typing import Dict, Any, List, Optional

from anus.core.agent.hybrid_agent import HybridAgent

class AgentOrchestrator:
    """
    Coordinates multiple agents and manages their lifecycle.
    """
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.agents: Dict[str, Any] = {}
        self.primary_agent = self._create_primary_agent()
        self.last_result: Dict[str, Any] = {}
        self.task_history: List[Dict[str, Any]] = []
        logging.info("ANUS Orchestrator initialized and ready for action")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        if not os.path.exists(config_path):
            logging.warning(f"Config file {config_path} not found. Using default configuration.")
            return {}
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            logging.info("ANUS configuration loaded successfully")
            return config
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return {}

    def _create_primary_agent(self) -> HybridAgent:
        # Здесь можно расширить создание агента, используя данные из конфигурации
        return HybridAgent(name="anus")

    async def execute_task(self, task: str, mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Asynchronously execute a task using the appropriate agent.
        Wraps the (possibly synchronous) primary_agent.execute call.
        """
        if mode is None:
            mode = self.config.get("agent", {}).get("mode", "single")
        start_time = time.time()
        logging.info(f"ANUS processing task: {task}")
        result = await self._async_execute(task, mode)
        execution_time = time.time() - start_time
        self.task_history.append({
            "task": task,
            "mode": mode,
            "start_time": start_time,
            "execution_time": execution_time,
            "status": "completed",
            "result": result
        })
        self.last_result = result
        logging.info(f"ANUS completed task in {execution_time:.2f}s")
        return result

    async def _async_execute(self, task: str, mode: str) -> Dict[str, Any]:
        """
        Wrap the synchronous primary_agent.execute method in a coroutine.
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.primary_agent.execute, task, mode=mode)
