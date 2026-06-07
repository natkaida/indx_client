"""
API клиент для INDX.MONEY
"""

import hashlib
import base64
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
import requests

from config_manager import ConfigManager


class ReqnManager:
    """Менеджер инкрементируемого reqn"""
    
    def __init__(self, filename: str = "reqn.txt"):
        self.filename = filename
        if not os.path.exists(filename):
            self._save(1)
    
    def _load(self) -> int:
        """Загрузка текущего значения reqn"""
        try:
            with open(self.filename, 'r') as f:
                return int(f.read().strip())
        except (ValueError, FileNotFoundError):
            return 1
    
    def _save(self, reqn: int):
        """Сохранение значения reqn"""
        with open(self.filename, 'w') as f:
            f.write(str(reqn))
    
    def get_next(self) -> int:
        """Получить следующий инкрементированный reqn"""
        current = self._load()
        next_reqn = current + 1
        self._save(next_reqn)
        return next_reqn


class IndxAPIClient:
    """Клиент для работы с API INDX.MONEY"""
    
    BASE_URL = "https://api.indx.money/api/v3/trade"
    COMMISSION_RATE = 0.0005  # Комиссия 0.05% в WMZ
    
    # Константы периодов для метода Tick
    KIND_DAY = 1
    KIND_WEEK = 2
    KIND_MONTH = 3
    KIND_YEAR = 4
    
    def __init__(self, config_file: str = "config.json", reqn_file: str = "reqn.txt"):
        """
        Инициализация API клиента
        
        Args:
            config_file: путь к файлу конфигурации
            reqn_file: путь к файлу с номером запроса
        """
        self.config = ConfigManager(config_file)
        self.reqn_manager = ReqnManager(reqn_file)
        
    
    def _generate_signature(self, params: List[str]) -> str:
        """
        Генерация подписи BASE64 + SHA256
        
        Args:
            params: список параметров для подписи
            
        Returns:
            строка подписи в формате BASE64
        """
        signature_string = ';'.join(str(p) for p in params)
        sha256_hash = hashlib.sha256(signature_string.encode('utf-8')).digest()
        return base64.b64encode(sha256_hash).decode('utf-8')
    
    def _make_request(self, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправка запроса к API
        
        Args:
            method: название метода API
            payload: тело запроса
            
        Returns:
            ответ API в виде словаря
        """
        url = f"{self.BASE_URL}/{method}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/json'
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {
                "code": -7,
                "desc": "Request timeout",
                "value": None
            }
        except requests.exceptions.ConnectionError:
            return {
                "code": -7,
                "desc": "Connection error",
                "value": None
            }
        except requests.exceptions.RequestException as e:
            return {
                "code": -7,


                "desc": f"Request error: {str(e)}",
                "value": None
            }
    
    @staticmethod
    def filter_portfolio(portfolio: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрация портфеля: оставляем только инструменты с количеством > 0
        
        Args:
            portfolio: список инструментов портфеля
            
        Returns:
            отфильтрованный список
        """
        if not portfolio:
            return []
        return [item for item in portfolio if item.get('notes', 0) > 0]
    
    @staticmethod
    def filter_tools_unique(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Фильтрация списка инструментов: оставляем только запись с наименьшим ID для каждого имени
        
        Args:
            tools: список инструментов
            
        Returns:
            отфильтрованный список
        """
        if not tools:
            return []
        
        tools_by_name = {}
        for tool in tools:
            name = tool.get('name', '')
            tool_id = tool.get('id', float('inf'))
            
            if name not in tools_by_name or tool_id < tools_by_name[name].get('id', float('inf')):
                tools_by_name[name] = tool
        
        return sorted(tools_by_name.values(), key=lambda x: x.get('id', 0))
    
    def calculate_order_cost(self, count: float, price: float, is_bid: bool) -> Dict[str, float]:
        """
        Расчет стоимости ордера с учетом комиссии 0.05%
        
        Args:
            count: количество (может быть дробным)
            price: цена за единицу
            is_bid: True - покупка, False - продажа
            
        Returns:
            словарь с деталями расчета
        """
        total_cost = count * price
        commission = total_cost * self.COMMISSION_RATE
        
        if is_bid:
            final_cost = total_cost + commission
        else:
            final_cost = total_cost - commission
        
        return {
            'total_cost': total_cost,
            'commission': commission,
            'final_cost': final_cost
        }
    
    # ==================== Методы API ====================
    
    def balance(self) -> Dict[str, Any]:
        """
        Метод Balance - текущий баланс трейдера
        Подпись: Login + ';' + Password + ';' + Culture + ';' + Wmid + ';' + Reqn
        
        Returns:
            ответ API с балансом и портфелем
        """
        reqn = self.reqn_manager.get_next()
        
        signature = self._generate_signature([
            self.config.login,
            self.config.password,
            self.config.culture,
            self.config.wmid,
            str(reqn)
        ])
        
        payload = {
            "ApiContext": {
                "Login": self.config.login,
                "Wmid": self.config.wmid,
                "Culture": self.config.culture,
                "Signature": signature,
                "Reqn": str(reqn)
            }
        }
        
        response = self._make_request("Balance", payload)
        
        if response.get('code') == 0 and 'value' in response:
            if response['value']:
                if 'portfolio' in response['value']:
                    response['value']['portfolio'] = self.filter_portfolio(
                        response['value']['portfolio']
                    )
                if 'profit' in response['value']:
                    del response['value']['profit']
        
        return response
    
    def tools(self, filter_unique: bool = True) -> Dict[str, Any]:
        """
        Метод Tools - список инструментов биржи
        Подпись: Login + ';' + Password + ';' + Culture + ';' + Reqn
        
        Args:
            filter_unique: если True, оставляет только запись с наименьшим ID для каждого имени
            
        Returns:
            ответ API со списком инструментов
        """
        reqn = self.reqn_manager.get_next()
        
        signature = self._generate_signature([
            self.config.login,
            self.config.password,
            self.config.culture,
            str(reqn)
        ])
        
        payload = {
            "ApiContext": {
                "Login": self.config.login,
                "Wmid": self.config.wmid,
                "Culture": self.config.culture,
                "Signature": signature,
                "Reqn": str(reqn)
            }
        }
        
        response = self._make_request("Tools", payload)
        
        if response.get('code') == 0 and filter_unique and 'value' in response:
            if isinstance(response['value'], list):
                response['value'] = self.filter_tools_unique(response['value'])
        
        return response
    
    def history_trading(self, tool_id: int = 0, date_start: str = None, date_end: str = None) -> Dict[str, Any]:
        """
        Метод HistoryTrading - история торгов трейдера
        Подпись: Login + ';' + Password + ';' + Culture + ';' + Wmid + ';' + ID + ';' + DateStart + ';' + DateEnd + ';' + Reqn
        
        Args:
            tool_id: ID инструмента (0 - все инструменты)
            date_start: начальная дата в формате YYYYMMDD
            date_end: конечная дата в формате YYYYMMDD
            
        Returns:
            ответ API с историей торгов
        """
        if date_start is None:
            date_start = datetime.now().replace(day=1).strftime("%Y%m%d")
        if date_end is None:
            date_end = datetime.now().strftime("%Y%m%d")
        
        reqn = self.reqn_manager.get_next()
        
        signature = self._generate_signature([
            self.config.login,
            self.config.password,
            self.config.culture,
            self.config.wmid,
            str(tool_id),
            date_start,
            date_end,
            str(reqn)
        ])
        
        payload = {
            "ApiContext": {
                "Login": self.config.login,
                "Wmid": self.config.wmid,
                "Culture": self.config.culture,
                "Signature": signature,
                "Reqn": str(reqn)
            },
            "Trading": {
                "ID": tool_id,
                "DateStart": date_start,
                "DateEnd": date_end
            }
        }
        
        return self._make_request("HistoryTrading", payload)
    
    def offer_my(self) -> Dict[str, Any]:
        """
        Метод OfferMy - список текущих заявок трейдера
        Подпись: Login + ';' + Password + ';' + Culture + ';' + Wmid + ';' + Reqn
        
        Returns:
            ответ API со списком заявок
        """
        reqn = self.reqn_manager.get_next()
        
        signature = self._generate_signature([
            self.config.login,
            self.config.password,
            self.config.culture,
            self.config.wmid,
            str(reqn)
        ])
        
        payload = {
            "ApiContext": {
                "Login": self.config.login,
                "Wmid": self.config.wmid,
                "Culture": self.config.culture,
                "Signature": signature,
                "Reqn": str(reqn)
            }
        }
        
        return self._make_request("OfferMy", payload)
    
    def offer_list(self, tool_id: int) -> Dict[str, Any]:
        """
        Метод OfferList - список заявок по инструменту
        Подпись: Login + ';' + Password + ';' + Culture + ';' + Wmid + ';' + ID + ';' + Reqn
        
        Args:
            tool_id: ID инструмента
            
        Returns:
            ответ API со списком заявок
        """
        reqn = self.reqn_manager.get_next()
        
        signature = self._generate_signature([
            self.config.login,
            self.config.password,
            self.config.culture,
            self.config.wmid,
            str(tool_id),
            str(reqn)
        ])
        
        payload = {
            "ApiContext": {
                "Login": self.config.login,
                "Wmid": self.config.wmid,
                "Culture": self.config.culture,
                "Signature": signature,
                "Reqn": str(reqn)
            },
            "Trading": {
                "ID": tool_id
            }
        }
        
        return self._make_request("OfferList", payload)
    
    def offer_add(self, tool_id: int, count: float, is_bid: bool, price: float, is_anonymous: bool = True) -> Dict[str, Any]:
        """
        Метод OfferAdd - создание новой заявки
        Подпись: Login + ';' + Password + ';' + Culture + ';' + Wmid + ';' + ID + ';' + Reqn
        
        Args:
            tool_id: ID инструмента
            count: количество (может быть дробным)
            is_bid: True - покупка, False - продажа
            price: цена за единицу
            is_anonymous: True - анонимная заявка
            
        Returns:
            ответ API с результатом создания
        """
        reqn = self.reqn_manager.get_next()
        
        signature = self._generate_signature([
            self.config.login,
            self.config.password,
            self.config.culture,
            self.config.wmid,
            str(tool_id),
            str(reqn)
        ])
        
        payload = {
            "ApiContext": {
                "Login": self.config.login,
                "Wmid": self.config.wmid,
                "Culture": self.config.culture,
                "Signature": signature,
                "Reqn": str(reqn)
            },
            "Offer": {
                "ID": tool_id,
                "Count": count,
                "IsAnonymous": is_anonymous,
                "IsBid": is_bid,
                "Price": price
            }
        }
        
        return self._make_request("OfferAdd", payload)
    
    def offer_delete(self, offer_id: int) -> Dict[str, Any]:
        """
        Метод OfferDelete - удаление заявки
        Подпись: Login + ';' + Password + ';' + Culture + ';' + Wmid + ';' + OfferID + ';' + Reqn
        
        Args:
            offer_id: ID заявки для удаления
            
        Returns:
            ответ API с результатом удаления
        """
        reqn = self.reqn_manager.get_next()
        
        signature = self._generate_signature([
            self.config.login,
            self.config.password,
            self.config.culture,
            self.config.wmid,
            str(offer_id),
            str(reqn)
        ])
        
        payload = {
            "ApiContext": {
                "Login": self.config.login,
                "Wmid": self.config.wmid,
                "Culture": self.config.culture,
                "Signature": signature,
                "Reqn": str(reqn)
            },
            "OfferId": offer_id
        }
        
        return self._make_request("OfferDelete", payload)
    
    def tick(self, tool_id: int, kind: int = 1) -> Dict[str, Any]:
        """
        Метод Tick - статистика сделок за период
        Подпись: Login + ';' + Password + ';' + Culture + ';' + Wmid + ';' + Tick/ID + ';' + Tick/Kind + ';' + Reqn
        
        Args:
            tool_id: ID инструмента
            kind: период (1 - день, 2 - неделя, 3 - месяц, 4 - год)
            
        Returns:
            ответ API со статистикой
        """
        if kind not in [self.KIND_DAY, self.KIND_WEEK, self.KIND_MONTH, self.KIND_YEAR]:
            raise ValueError(f"Invalid kind={kind}. Must be 1-4")
        
        reqn = self.reqn_manager.get_next()
        
        signature = self._generate_signature([
            self.config.login,
            self.config.password,
            self.config.culture,
            self.config.wmid,
            str(tool_id),
            str(kind),
            str(reqn)
        ])
        
        payload = {
            "ApiContext": {
                "Login": self.config.login,
                "Wmid": self.config.wmid,
                "Culture": self.config.culture,
                "Signature": signature,
                "Reqn": str(reqn)
            },
            "Tick": {
                "ID": tool_id,
                "Kind": kind
            }
        }
        
        return self._make_request("Tick", payload)