from typing import Dict, List, Any, Optional, Union, Type
import logging

from anus.models.base.base_model import BaseModel
from anus.models.openai_model import OpenAIModel
from anus.models.gemini_model import GeminiModel  # Добавлен импорт GeminiModel

class ModelRouter:
    """
    Роутер для динамического выбора и управления языковыми моделями.
    """
    
    def __init__(self, default_model_config: Optional[Dict[str, Any]] = None):
        self.models: Dict[str, BaseModel] = {}
        self.model_classes: Dict[str, Type[BaseModel]] = {
            "openai": OpenAIModel,
            "gemini": GeminiModel,  # Поддержка Gemini
        }
        self.default_model_config = default_model_config or {
            "provider": "openai",
            "model_name": "gpt-4o",
            "temperature": 0.0
        }
        self.default_model = None
    
    def register_model(self, name: str, model: BaseModel) -> None:
        self.models[name] = model
        logging.info(f"Registered model: {name}")
    
    def register_model_class(self, provider: str, model_class: Type[BaseModel]) -> None:
        self.model_classes[provider] = model_class
        logging.info(f"Registered model class for provider: {provider}")
    
    def get_model(self, name_or_config: Union[str, Dict[str, Any]]) -> BaseModel:
        if isinstance(name_or_config, str):
            if name_or_config in self.models:
                return self.models[name_or_config]
            logging.warning(f"Model '{name_or_config}' not found. Using default model.")
            return self.get_default_model()
        elif isinstance(name_or_config, dict):
            return self._create_model_from_config(name_or_config)
        else:
            logging.error(f"Invalid model specification: {name_or_config}")
            return self.get_default_model()
    
    def get_default_model(self) -> BaseModel:
        if self.default_model is None:
            self.default_model = self._create_model_from_config(self.default_model_config)
        return self.default_model
    
    def select_model_for_task(self, task: str, requirements: Dict[str, Any] = None) -> BaseModel:
        if requirements:
            return self._create_model_from_config(requirements)
        return self.get_default_model()
    
    def _create_model_from_config(self, config: Dict[str, Any]) -> BaseModel:
        provider = config.get("provider", "openai").lower()
        if provider not in self.model_classes:
            logging.error(f"Unknown model provider: {provider}. Using OpenAI as fallback.")
            provider = "openai"
        try:
            model_class = self.model_classes[provider]
            kwargs = config.copy()
            kwargs.pop("provider", None)
            return model_class(**kwargs)
        except Exception as e:
            logging.error(f"Error creating model for provider {provider}: {e}")
            try:
                return OpenAIModel(model_name="gpt-4o")
            except Exception:
                raise ValueError(f"Failed to create model: {e}")
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        models_info = []
        for name, model in self.models.items():
            info = {
                "name": name,
                "type": type(model).__name__,
                "model_name": model.model_name,
                "details": model.get_model_details()
            }
            models_info.append(info)
        for provider in self.model_classes.keys():
            if provider not in [info["details"].get("provider") for info in models_info]:
                models_info.append({
                    "name": f"{provider}",
                    "type": self.model_classes[provider].__name__,
                    "details": {"provider": provider}
                })
        return models_info
