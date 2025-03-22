"""
Hybrid Agent module that combines single and multi-agent capabilities.

This agent can dynamically switch between single and multi-agent modes based on task complexity.
"""

import logging
import re
from typing import Dict, Any, List, Tuple, Optional

from anus.core.agent.tool_agent import ToolAgent

class HybridAgent(ToolAgent):
    """
    A hybrid agent that can switch between single and multi-agent modes.
    
    This agent assesses task complexity and chooses the appropriate mode.
    """
    
    def __init__(
        self,
        name: Optional[str] = None,
        max_iterations: int = 10,
        tools: Optional[List[str]] = None,
        **kwargs
    ):
        """
        Initialize a HybridAgent instance.
        
        Args:
            name: Optional name for the agent.
            max_iterations: Maximum number of thought-action cycles to perform.
            tools: Optional list of tool names to load.
            **kwargs: Additional configuration options for the agent.
        """
        super().__init__(name=name, max_iterations=max_iterations, tools=tools, **kwargs)
        self.mode = "auto"
        
        # Initialize dictionary to hold specialized agents for multi-agent mode.
        # Initially, no specialized agents are created.
        self.specialized_agents = {
            "researcher": None,
            "planner": None,
            "executor": None,
            "critic": None
        }
    
    def add_specialized_agent(self, role: str, config: dict) -> None:
        """
        Создает и регистрирует специализированного агента для заданной роли.
        
        Args:
            role: Роль агента (например, "researcher", "planner", "executor", "critic").
            config: Конфигурация агента для данной роли.
        
        Данный метод создает нового агента (на базе ToolAgent) с указанными настройками и сохраняет его в словаре specialized_agents.
        """
        from anus.core.agent.tool_agent import ToolAgent  # Импортируем класс инструментарного агента
        agent_name = config.get("name", f"{role}-agent")
        specialized_agent = ToolAgent(name=agent_name, **config)
        self.specialized_agents[role] = specialized_agent
        logging.info(f"Added specialized agent for role '{role}' with name '{agent_name}'")
    
    def _assess_complexity(self, task: str) -> float:
        """
        Assess the complexity of a task.
        
        Args:
            task: The task description.
            
        Returns:
            A complexity score between 0 and 10.
        """
        complexity = 0.0
        
        # Check for multiple operations
        operations = [
            (r'(calculate|compute|evaluate)', 1.0),
            (r'(search|find|look up)', 1.0),
            (r'(count|process|analyze|transform)\s+text', 1.0),
            (r'run\s+code|execute', 1.5),
            (r'compare|contrast|evaluate', 2.0),
            (r'optimize|improve|enhance', 2.5),
            (r'and|then|after|before', 1.0),
            (r'if|when|unless|otherwise', 1.5),
            (r'all|every|each', 1.0),
            (r'most|best|optimal', 1.5)
        ]
        
        for pattern, score in operations:
            matches = re.findall(pattern, task.lower())
            complexity += score * len(matches)
        
        words = task.split()
        complexity += len(words) * 0.1
        
        special_chars = sum(1 for c in task if not c.isalnum() and not c.isspace())
        complexity += special_chars * 0.2
        
        tool_keywords = {
            'calculator': ['calculate', 'compute', 'evaluate', 'math'],
            'search': ['search', 'find', 'look up', 'query'],
            'text': ['text', 'string', 'characters', 'words'],
            'code': ['code', 'execute', 'run', 'python']
        }
        
        tools_needed = 0
        task_lower = task.lower()
        for tool_name, keywords in tool_keywords.items():
            if any(kw in task_lower for kw in keywords):
                tools_needed += 1
            
        complexity += tools_needed * 1.5
        
        return min(10.0, complexity)
    
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task using the appropriate mode based on complexity.
        
        Args:
            task: The task description to execute.
            **kwargs: Additional parameters for task execution.
            
        Returns:
            A dictionary containing the execution result and metadata.
        """
        complexity = self._assess_complexity(task)
        
        if complexity < 3.0:
            logging.info(f"Task complexity ({complexity:.1f}) below threshold (3.0). ANUS staying tight in single-agent mode.")
            logging.info("This task is so simple even a constipated ANUS could handle it.")
            return super().execute(task, **kwargs)
        else:
            logging.info(f"Task complexity ({complexity:.1f}) above threshold (3.0). ANUS expanding to multi-agent mode.")
            logging.info("ANUS is expanding to accommodate multiple agents for this complex task.")
            return self._execute_multi_agent(task, **kwargs)
    
    def _execute_multi_agent(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a task using multiple specialized agents.
        
        Args:
            task: The task description to execute.
            **kwargs: Additional parameters for task execution.
            
        Returns:
            A dictionary containing the aggregated results.
        """
        logging.info("ANUS expanding to accommodate multiple agents")
        logging.info("Task decomposed into subtasks for optimal ANUS performance")
        
        # Пример для простых математических операций
        if task.lower().startswith("calculate"):
            action_name, action_input = self._decide_action({"task": task})
            if action_name == "calculator" and "expression" in action_input:
                result = self._execute_action(action_name, action_input)
                if result.get("status") == "success" and "result" in result:
                    return {
                        "task": task,
                        "answer": f"The result of {action_input['expression']} is {result['result']}",
                        "direct_result": result,
                        "mode": "direct"
                    }
        
        results = {}
        final_result = None
        
        # Если специализированные агенты ещё не созданы, их можно создать здесь
        standard_roles = ["researcher", "planner", "executor", "critic"]
        for role in standard_roles:
            if not self.specialized_agents.get(role):
                # Пример: используем конфигурацию по умолчанию для каждого агента
                default_config = {"name": f"{role}-agent", "tools": kwargs.get("tools", [])}
                self.add_specialized_agent(role, default_config)
        
        # Выполнение задачи специализированными агентами
        if self.specialized_agents.get("researcher"):
            results["researcher"] = self.specialized_agents["researcher"].execute(
                f"Analyze and gather information for: {task}"
            )
        
        if self.specialized_agents.get("planner"):
            results["planner"] = self.specialized_agents["planner"].execute(
                f"Plan execution strategy for: {task}\nBased on research: {results.get('researcher')}"
            )
        
        if self.specialized_agents.get("executor"):
            results["executor"] = self.specialized_agents["executor"].execute(
                f"Execute plan for: {task}\nFollowing strategy: {results.get('planner')}"
            )
            final_result = results["executor"]
        
        if self.specialized_agents.get("critic"):
            results["critic"] = self.specialized_agents["critic"].execute(
                f"Evaluate results for: {task}\nAnalyzing output: {results.get('executor')}"
            )
        
        logging.info("All agents have finished their tasks. ANUS is aggregating results...")
        logging.info("ANUS has successfully completed multi-agent processing")
        
        return {
            "task": task,
            "answer": final_result.get("answer", str(final_result)) if final_result else "No answer",
            "agent_results": results,
            "mode": "multi"
        }
