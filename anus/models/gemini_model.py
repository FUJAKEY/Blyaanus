from typing import Dict, List, Optional, Union
import os
import logging
import asyncio

# Импортируем библиотеку Gemini из Google GenAI
from google import genai
from google.genai import types

from anus.models.base.base_model import BaseModel, Message, ModelResponse, ToolCall

class GeminiModel(BaseModel):
    """
    Gemini API integration для языковых моделей.
    
    Использует модель "gemini-2.0-flash" от Google GenAI.
    """
    provider: str = "gemini"
    model_name: str = "gemini-2.0-flash"
    api_key: Optional[str] = os.environ.get("GEMINI_API_KEY")
    base_url: Optional[str] = None  # Можно указать нестандартный endpoint, если требуется
    temperature: float = 0.0
    max_tokens: int = 4096

    async def ask(
        self, 
        messages: List[Union[Dict, Message]], 
        system_message: Optional[str] = None,
        **kwargs
    ) -> ModelResponse:
        """
        Отправляет запрос в Gemini API и получает ответ.
        
        Для обеспечения асинхронности оборачиваем синхронный вызов в asyncio.
        """
        # Формируем текст запроса: объединяем системное сообщение и остальные сообщения
        prompt = ""
        if system_message:
            prompt += system_message + "\n"
        for msg in messages:
            if isinstance(msg, dict):
                prompt += msg.get("content", "") + "\n"
            else:
                prompt += msg.content + "\n"
        
        # Инициализируем клиента Gemini
        client = genai.Client(api_key=self.api_key)
        
        # Создаем конфигурацию для запроса
        config = types.GenerateContentConfig(
            system_instruction=system_message or ""
        )
        
        # Выполняем запрос в отдельном потоке, чтобы не блокировать event loop
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=self.model_name,
                config=config,
                contents=prompt
            )
        )
        
        # Возвращаем результат в виде ModelResponse (используем response.text)
        return ModelResponse(content=response.text)

    async def ask_with_tools(
        self,
        messages: List[Union[Dict, Message]],
        system_message: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto",
        **kwargs
    ) -> ModelResponse:
        """
        Gemini API не поддерживает вызовы функций (tool calling) «из коробки».
        Поэтому используем тот же метод ask.
        """
        return await self.ask(messages, system_message=system_message, **kwargs)
