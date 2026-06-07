"""
Менеджер конфигурации для INDX.MONEY API
"""

import json
import os
from typing import Any, Dict, Optional


class ConfigManager:
    """Менеджер конфигурации трейдера"""
    
    def __init__(self, filename: str = "config.json"):
        self.filename = filename
        self.config = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Загрузка конфигурации из файла"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file {self.filename} not found!")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def get(self, key: str, default=None) -> Any:
        """Получить значение из конфигурации"""
        return self.config.get(key, default)
    
    @property
    def login(self) -> str:
        """Логин трейдера"""
        return self.config['login']
    
    @property
    def password(self) -> str:
        """Пароль трейдера"""
        return self.config['password']
    
    @property
    def wmid(self) -> str:
        """WMID трейдера"""
        return self.config['wmid']
    
    @property
    def culture(self) -> str:
        """Язык запросов (ru-RU, en-EN)"""
        return self.config.get('culture', 'ru-RU')
    
    
    def validate(self) -> bool:
        """Проверка обязательных полей конфигурации"""
        required_fields = ['login', 'password', 'wmid']
        for field in required_fields:
            if field not in self.config:
                return False
        return True