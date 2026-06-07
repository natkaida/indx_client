"""
Графический интерфейс для INDX.MONEY API
"""

import threading
from datetime import datetime
from tkinter import messagebox, ttk
import customtkinter as ctk

from api_client import IndxAPIClient


class BalanceManager:
    """Менеджер состояния баланса"""
    
    def __init__(self):
        self.wmid = ""
        self.nickname = ""
        self.portfolio_price = 0.0
        self.total_wmz = 0.0
        self.available = 0.0
        self.blocked = 0.0
        self.loaded = False
    
    def update_from_api(self, response: dict):
        """Обновление данных из ответа API"""
        if response.get('code') == 0 and response.get('value'):
            value = response['value']
            balance = value.get('balance', {})
            
            self.wmid = value.get('wmid', 'N/A')
            self.nickname = value.get('nickname', 'N/A')
            self.portfolio_price = balance.get('price', 0)
            self.total_wmz = balance.get('wmz', 0)
            self.available = balance.get('available', self.total_wmz)
            self.blocked = self.total_wmz - self.available
            self.loaded = True
            return True
        return False
    
    def block_funds(self, amount: float):
        """Заблокировать средства при создании ордера на покупку"""
        self.available -= amount
        self.blocked += amount
    
    def unblock_funds(self, amount: float):
        """Разблокировать средства при удалении ордера на покупку"""
        self.blocked -= amount
        self.available += amount
        if self.blocked < 0:
            self.blocked = 0
    
    def get_display_text(self) -> str:
        """Получить текст для отображения баланса"""
        if not self.loaded:
            return "Загрузка баланса..."
        
        text = f"Трейдер: {self.nickname}\n"
        text += f"WMID: {self.wmid}\n\n"
        text += f"💰 Стоимость портфеля: {self.portfolio_price:.4f} WMZ\n"
        text += f"💵 Всего средств (WMZ): {self.total_wmz:.4f} WMZ\n"
        text += f"✅ Доступно для торгов: {self.available:.4f} WMZ\n"
        
        if self.blocked > 0:
            text += f"🔒 Заблокировано в ордерах: {self.blocked:.4f} WMZ"
        
        return text


class IndxGUI:
    """Графический интерфейс для INDX.MONEY API"""
    
    def __init__(self):
        # Настройка темы
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Создание главного окна
        self.root = ctk.CTk()
        self.root.title("INDX.MONEY Trading Client")
        self.root.geometry("1200x800")
        
        # Инициализация API клиента
        try:
            self.api = IndxAPIClient()
        except FileNotFoundError as e:
            messagebox.showerror("Ошибка", str(e))
            self.root.destroy()
            return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка инициализации: {str(e)}")
            self.root.destroy()
            return
        
        # Менеджер баланса
        self.balance = BalanceManager()
        
        # Создание GUI
        self._create_widgets()
        
        # Загрузка начальных данных
        self._load_initial_data()
    
    def _create_widgets(self):
        """Создание всех виджетов интерфейса"""
        self._create_header()
        self._create_tabs()
    
    def _create_header(self):
        """Создание верхней панели"""
        self.header_frame = ctk.CTkFrame(self.root, height=60)
        self.header_frame.pack(fill="x", padx=5, pady=5)
        
        
        self.wmid_label = ctk.CTkLabel(
            self.header_frame,
            text=f"INDX.MONEY Trading Client | WMID: {self.api.config.wmid}",
            font=("Arial", 16, "bold")
        )
        self.wmid_label.pack(side="left", padx=20)
        
        self.status_label = ctk.CTkLabel(
            self.header_frame,
            text="Готов к работе",
            font=("Arial", 12),
            text_color="gray"
        )
        self.status_label.pack(side="right", padx=20)
    
    def _create_tabs(self):
        """Создание вкладок"""
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tabview.add("Баланс и ордера")
        self.tabview.add("Инструменты")
        self.tabview.add("История торгов")
        self.tabview.add("Заявки по инструменту")
        self.tabview.add("Статистика (Tick)")
        
        self._create_balance_tab()
        self._create_tools_tab()
        self._create_history_tab()
        self._create_offer_list_tab()
        self._create_tick_tab()
    
    def _configure_tree_style(self):
        """Настройка стиля для таблиц"""
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        rowheight=25)
        style.configure("Treeview.Heading",
                        background="#1f1f1f",
                        foreground="white",
                        relief="flat")
        style.map("Treeview", background=[("selected", "#1f538d")])
    
    def _create_balance_tab(self):
        """Создание вкладки баланса и ордеров"""
        tab = self.tabview.tab("Баланс и ордера")
        
        # Левая панель - баланс и портфель
        left_frame = ctk.CTkFrame(tab)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Баланс
        balance_frame = ctk.CTkFrame(left_frame)
        balance_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(balance_frame, text="БАЛАНС", font=("Arial", 18, "bold")).pack(pady=5)
        
        self.balance_info = ctk.CTkLabel(
            balance_frame,
            text="Загрузка баланса...",
            font=("Arial", 14),
            justify="left"
        )
        self.balance_info.pack(pady=10)
        
        # Портфель
        portfolio_frame = ctk.CTkFrame(left_frame)
        portfolio_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(portfolio_frame, text="ПОРТФЕЛЬ", font=("Arial", 18, "bold")).pack(pady=5)
        
        tree_frame = ctk.CTkFrame(portfolio_frame, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._configure_tree_style()
        
        self.portfolio_tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Name", "Type", "Count", "Price"),
            show="headings",
            height=8
        )
        
        for col, text, width, anchor in [
            ("ID", "ID", 60, "center"),
            ("Name", "Название", 120, "w"),
            ("Type", "Тип", 80, "center"),
            ("Count", "Кол-во", 80, "center"),
            ("Price", "Цена", 100, "e")
        ]:
            self.portfolio_tree.heading(col, text=text)
            self.portfolio_tree.column(col, width=width, anchor=anchor)
        
        portfolio_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.portfolio_tree.yview)
        self.portfolio_tree.configure(yscrollcommand=portfolio_scroll.set)
        self.portfolio_tree.pack(side="left", fill="both", expand=True)
        portfolio_scroll.pack(side="right", fill="y")
        
        # Правая панель - ордера
        right_frame = ctk.CTkFrame(tab)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Ордера
        orders_frame = ctk.CTkFrame(right_frame)
        orders_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(orders_frame, text="АКТИВНЫЕ ОРДЕРА", font=("Arial", 18, "bold")).pack(pady=5)
        
        orders_tree_frame = ctk.CTkFrame(orders_frame, fg_color="transparent")
        orders_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.orders_tree = ttk.Treeview(
            orders_tree_frame,
            columns=("OfferID", "ToolID", "Name", "Type", "Price", "Count", "Cost"),
            show="headings",
            height=8
        )
        
        for col, text, width, anchor in [
            ("OfferID", "Offer ID", 70, "center"),
            ("ToolID", "Tool ID", 70, "center"),
            ("Name", "Название", 100, "w"),
            ("Type", "Тип", 70, "center"),
            ("Price", "Цена", 90, "e"),
            ("Count", "Кол-во", 70, "center"),
            ("Cost", "Стоимость", 100, "e")
        ]:
            self.orders_tree.heading(col, text=text)
            self.orders_tree.column(col, width=width, anchor=anchor)
        
        orders_scroll = ttk.Scrollbar(orders_tree_frame, orient="vertical", command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=orders_scroll.set)
        self.orders_tree.pack(side="left", fill="both", expand=True)
        orders_scroll.pack(side="right", fill="y")
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(right_frame)
        buttons_frame.pack(fill="x", padx=5, pady=5)
        
        self.buy_btn = ctk.CTkButton(
            buttons_frame, text="📈 Купить",
            command=lambda: self._create_order_dialog(True),
            fg_color="#006400", hover_color="#008000",
            height=40, font=("Arial", 14, "bold")
        )
        self.buy_btn.pack(pady=5, padx=10, fill="x")
        
        self.sell_btn = ctk.CTkButton(
            buttons_frame, text="📉 Продать",
            command=lambda: self._create_order_dialog(False),
            fg_color="#8B0000", hover_color="#A00000",
            height=40, font=("Arial", 14, "bold")
        )
        self.sell_btn.pack(pady=5, padx=10, fill="x")
        
        self.delete_order_btn = ctk.CTkButton(
            buttons_frame, text="🗑️ Удалить ордер",
            command=self._delete_order,
            fg_color="#555555", hover_color="#666666",
            height=40, font=("Arial", 14)
        )
        self.delete_order_btn.pack(pady=5, padx=10, fill="x")
    
    def _create_tools_tab(self):
        """Создание вкладки инструментов"""
        tab = self.tabview.tab("Инструменты")
        
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(control_frame, text="СПИСОК ИНСТРУМЕНТОВ БИРЖИ", font=("Arial", 18, "bold")).pack(
            side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            control_frame, text="🔄 Обновить список",
            command=self._refresh_tools, width=150
        ).pack(side="right", padx=10, pady=10)
        
        table_frame = ctk.CTkFrame(tab)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tools_tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Price"),
            show="headings"
        )
        
        for col, text, width in [
            ("ID", "ID", 80), ("Name", "Название", 150),
            ("Price", "Цена", 120)
        ]:
            self.tools_tree.heading(col, text=text)
            self.tools_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tools_tree.yview)
        self.tools_tree.configure(yscrollcommand=scrollbar.set)
        self.tools_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
    
    def _create_history_tab(self):
        """Создание вкладки истории торгов"""
        tab = self.tabview.tab("История торгов")
        
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(control_frame, text="ИСТОРИЯ ТОРГОВ", font=("Arial", 18, "bold")).pack(
            side="left", padx=10, pady=10)
        
        params_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        params_frame.pack(side="right", padx=5)
        
        ctk.CTkLabel(params_frame, text="ID:").pack(side="left", padx=2)
        self.history_tool_id = ctk.CTkEntry(params_frame, width=80)
        self.history_tool_id.pack(side="left", padx=2)
        self.history_tool_id.insert(0, "0")
        
        ctk.CTkLabel(params_frame, text="С:").pack(side="left", padx=2)
        self.history_date_start = ctk.CTkEntry(params_frame, width=100)
        self.history_date_start.pack(side="left", padx=2)
        
        ctk.CTkLabel(params_frame, text="По:").pack(side="left", padx=2)
        self.history_date_end = ctk.CTkEntry(params_frame, width=100)
        self.history_date_end.pack(side="left", padx=2)
        
        ctk.CTkButton(params_frame, text="🔍 Поиск", command=self._refresh_history, width=80).pack(
            side="left", padx=5)
        
        table_frame = ctk.CTkFrame(tab)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.history_tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Date", "Name", "Type", "Count", "Price"),
            show="headings"
        )
        
        for col, text, width in [
            ("ID", "ID", 80), ("Date", "Дата", 150), ("Name", "Название", 150),
            ("Type", "Тип", 100), ("Count", "Кол-во", 100), ("Price", "Цена", 120)
        ]:
            self.history_tree.heading(col, text=text)
            self.history_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        self.history_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
    
    def _create_offer_list_tab(self):
        """Создание вкладки заявок по инструменту"""
        tab = self.tabview.tab("Заявки по инструменту")
        
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(control_frame, text="ЗАЯВКИ ПО ИНСТРУМЕНТУ", font=("Arial", 18, "bold")).pack(
            side="left", padx=10, pady=10)
        
        params_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        params_frame.pack(side="right", padx=5)
        
        ctk.CTkLabel(params_frame, text="ID инструмента:").pack(side="left", padx=2)
        self.offer_tool_id = ctk.CTkEntry(params_frame, width=100)
        self.offer_tool_id.pack(side="left", padx=2)
        
        ctk.CTkButton(params_frame, text="🔍 Поиск", command=self._refresh_offer_list, width=80).pack(
            side="left", padx=5)
        
        table_frame = ctk.CTkFrame(tab)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.offers_tree = ttk.Treeview(
            table_frame,
            columns=("OfferID", "Type", "Price", "Count", "IsMy"),
            show="headings"
        )
        
        for col, text, width in [
            ("OfferID", "Offer ID", 100), ("Type", "Тип", 100),
            ("Price", "Цена", 120), ("Count", "Кол-во", 100), ("IsMy", "Моя заявка", 100)
        ]:
            self.offers_tree.heading(col, text=text)
            self.offers_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.offers_tree.yview)
        self.offers_tree.configure(yscrollcommand=scrollbar.set)
        self.offers_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
    
    def _create_tick_tab(self):
        """Создание вкладки статистики Tick"""
        tab = self.tabview.tab("Статистика (Tick)")
        
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(control_frame, text="СТАТИСТИКА СДЕЛОК (TICK)", font=("Arial", 18, "bold")).pack(
            side="left", padx=10, pady=10)
        
        params_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        params_frame.pack(side="right", padx=5)
        
        ctk.CTkLabel(params_frame, text="ID:").pack(side="left", padx=2)
        self.tick_tool_id = ctk.CTkEntry(params_frame, width=80)
        self.tick_tool_id.pack(side="left", padx=2)
        
        ctk.CTkLabel(params_frame, text="Период:").pack(side="left", padx=2)
        self.tick_period = ctk.CTkOptionMenu(params_frame, values=["День", "Неделя", "Месяц", "Год"], width=100)
        self.tick_period.pack(side="left", padx=2)
        
        ctk.CTkButton(params_frame, text="🔍 Поиск", command=self._refresh_tick, width=80).pack(
            side="left", padx=5)
        
        table_frame = ctk.CTkFrame(tab)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tick_tree = ttk.Treeview(
            table_frame,
            columns=("Date", "Min", "Max", "Open", "Close", "Avg", "Total"),
            show="headings"
        )
        
        for col in ["Date", "Min", "Max", "Open", "Close", "Avg", "Total"]:
            self.tick_tree.heading(col, text=col)
            self.tick_tree.column(col, width=110)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tick_tree.yview)
        self.tick_tree.configure(yscrollcommand=scrollbar.set)
        self.tick_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)
    
    # ==================== Методы обновления данных ====================
    
    def _update_status(self, text: str):
        """Обновление статусной строки"""
        self.status_label.configure(text=text)
    
    def _run_async(self, target, *args, **kwargs):
        """Запуск функции в отдельном потоке"""
        thread = threading.Thread(target=target, args=args, kwargs=kwargs, daemon=True)
        thread.start()
    
    def _load_initial_data(self):
        """Загрузка начальных данных"""
        def fetch():
            self.root.after(0, self._update_status, "Загрузка данных...")
            
            response = self.api.balance()
            self.root.after(0, self._update_balance_display, response)
            
            orders_response = self.api.offer_my()
            self.root.after(0, self._update_orders_display, orders_response)
            self.root.after(100, self._recalculate_blocked_from_orders)
            self.root.after(0, self._update_status, "Готов к работе")
        
        self._run_async(fetch)
    
    def _update_balance_display(self, response: dict):
        """Обновление отображения баланса"""
        if self.balance.update_from_api(response):
            # Очистка и заполнение портфеля
            for item in self.portfolio_tree.get_children():
                self.portfolio_tree.delete(item)
            
            portfolio = response.get('value', {}).get('portfolio', [])
            for item in portfolio:
                self.portfolio_tree.insert("", "end", values=(
                    item.get('id', 0), item.get('name', 'N/A'),
                    item.get('type', 'N/A'), f"{item.get('notes', 0):.4f}",
                    f"{item.get('price', 0):.4f}"
                ))
        else:
            self.balance_info.configure(
                text=f"Ошибка загрузки баланса: {response.get('desc', 'Unknown error')}")
        
        self._refresh_balance_display()
    
    def _refresh_balance_display(self):
        """Обновление текста баланса"""
        self.balance_info.configure(text=self.balance.get_display_text())
    
    def _recalculate_blocked_from_orders(self):
        """Пересчет заблокированных средств на основе ордеров"""
        total_blocked = 0.0
        for item in self.orders_tree.get_children():
            values = self.orders_tree.item(item)['values']
            if values[3] == "Покупка":
                try:
                    total_blocked += float(values[6])
                except (ValueError, IndexError):
                    pass
        
        self.balance.blocked = total_blocked
        self.balance.available = self.balance.total_wmz - total_blocked
        if self.balance.available < 0:
            self.balance.available = 0
        
        self._refresh_balance_display()
    
    def _update_orders_display(self, response: dict):
        """Обновление отображения ордеров"""
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        if response.get('code') == 0 and response.get('value'):
            for order in response['value']:
                order_type = "Покупка" if order.get('kind', 0) == 1 else "Продажа"
                price = order.get('price', 0)
                notes = order.get('notes', 0)
                cost = price * notes
                if order_type == "Покупка":
                    cost += cost * self.api.COMMISSION_RATE
                
                self.orders_tree.insert("", "end", values=(
                    order.get('offerid', 0), order.get('toolid', 0),
                    order.get('name', 'N/A'), order_type,
                    f"{price:.4f}", f"{notes:.4f}", f"{cost:.4f}"
                ))
    
    def _refresh_balance(self):
        """Обновление баланса"""
        def fetch():
            self.root.after(0, self._update_status, "Обновление баланса...")
            response = self.api.balance()
            self.root.after(0, self._update_balance_display, response)
            self.root.after(100, self._recalculate_blocked_from_orders)
            self.root.after(0, self._update_status, "Готов к работе")
        
        self._run_async(fetch)
    
    def _refresh_orders(self):
        """Обновление ордеров"""
        def fetch():
            self.root.after(0, self._update_status, "Обновление ордеров...")
            response = self.api.offer_my()
            self.root.after(0, self._update_orders_display, response)
            self.root.after(0, self._update_status, "Готов к работе")
        
        self._run_async(fetch)
    
    def _refresh_tools(self):
        """Обновление списка инструментов"""
        def fetch():
            self.root.after(0, self._update_status, "Загрузка инструментов...")
            response = self.api.tools(filter_unique=True)
            self.root.after(0, lambda: self._update_tools_display(response))
            self.root.after(0, self._update_status, "Готов к работе")
        
        self._run_async(fetch)
    
    def _update_tools_display(self, response: dict):
        """Обновление отображения инструментов"""
        for item in self.tools_tree.get_children():
            self.tools_tree.delete(item)
        
        if response.get('code') == 0 and isinstance(response.get('value'), list):
            for tool in response['value']:
                self.tools_tree.insert("", "end", values=(
                    tool.get('id', 0), tool.get('name', 'N/A'),
                    f"{tool.get('price', 0):.4f}", tool.get('kind', 0),
                    tool.get('type', 'N/A')
                ))
    
    def _refresh_history(self):
        """Обновление истории торгов"""
        def fetch():
            self.root.after(0, self._update_status, "Загрузка истории...")
            tool_id = int(self.history_tool_id.get() or "0")
            date_start = self.history_date_start.get() or None
            date_end = self.history_date_end.get() or None
            
            response = self.api.history_trading(tool_id, date_start, date_end)
            self.root.after(0, lambda: self._update_history_display(response))
            self.root.after(0, self._update_status, "Готов к работе")
        
        self._run_async(fetch)
    
    def _update_history_display(self, response: dict):
        """Обновление отображения истории"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        if response.get('code') == 0 and isinstance(response.get('value'), list):
            for trade in response['value']:
                stamp = trade.get('stamp', 0)
                date_str = datetime.fromtimestamp(stamp).strftime("%Y-%m-%d %H:%M:%S") if stamp else "N/A"
                trade_type = "Покупка" if trade.get('isbid', 0) == 1 else "Продажа"
                
                self.history_tree.insert("", "end", values=(
                    trade.get('id', 0), date_str, trade.get('name', 'N/A'),
                    trade_type, f"{trade.get('notes', 0):.4f}",
                    f"{trade.get('price', 0):.4f}"
                ))
    
    def _refresh_offer_list(self):
        """Обновление заявок по инструменту"""
        def fetch():
            self.root.after(0, self._update_status, "Загрузка заявок...")
            tool_id = self.offer_tool_id.get()
            if tool_id:
                response = self.api.offer_list(int(tool_id))
                self.root.after(0, lambda: self._update_offers_display(response))
            self.root.after(0, self._update_status, "Готов к работе")
        
        self._run_async(fetch)
    
    def _update_offers_display(self, response: dict):
        """Обновление отображения заявок"""
        for item in self.offers_tree.get_children():
            self.offers_tree.delete(item)
        
        if response.get('code') == 0 and isinstance(response.get('value'), list):
            for offer in response['value']:
                offer_type = "Покупка" if offer.get('kind', 0) == 1 else "Продажа"
                is_my = "Да" if offer.get('ismy', 0) == 1 else "Нет"
                
                self.offers_tree.insert("", "end", values=(
                    offer.get('offerid', 0), offer_type,
                    f"{offer.get('price', 0):.4f}",
                    f"{offer.get('notes', 0):.4f}", is_my
                ))
    
    def _refresh_tick(self):
        """Обновление статистики Tick"""
        def fetch():
            self.root.after(0, self._update_status, "Загрузка статистики...")
            tool_id = self.tick_tool_id.get()
            if tool_id:
                period_map = {"День": 1, "Неделя": 2, "Месяц": 3, "Год": 4}
                period = period_map.get(self.tick_period.get(), 1)
                try:
                    response = self.api.tick(int(tool_id), period)
                    self.root.after(0, lambda: self._update_tick_display(response))
                except ValueError as e:
                    self.root.after(0, messagebox.showerror, "Ошибка", str(e))
            self.root.after(0, self._update_status, "Готов к работе")
        
        self._run_async(fetch)
    
    def _update_tick_display(self, response: dict):
        """Обновление отображения статистики"""
        for item in self.tick_tree.get_children():
            self.tick_tree.delete(item)
        
        if response.get('code') == 0 and isinstance(response.get('value'), list):
            for tick in response['value']:
                t = tick.get('t', 0)
                date_str = datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M") if t else "N/A"
                
                self.tick_tree.insert("", "end", values=(
                    date_str, f"{tick.get('min', 0):.4f}",
                    f"{tick.get('max', 0):.4f}", f"{tick.get('open', 0):.4f}",
                    f"{tick.get('close', 0):.4f}", f"{tick.get('avg', 0):.4f}",
                    tick.get('total', 0)
                ))
    
    # ==================== Диалог создания ордера ====================
    
    def _create_order_dialog(self, is_bid: bool):
        """Диалог создания ордера"""
        if not self.balance.loaded:
            messagebox.showwarning("Предупреждение",
                                   "Баланс еще не загружен.\nПожалуйста, подождите.")
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Покупка" if is_bid else "Продажа")
        dialog.geometry("450x480")
        dialog.resizable(False, False)
        
        # Центрирование
        dialog.update_idletasks()
        w, h = 450, 480
        x = (dialog.winfo_screenwidth() // 2) - (w // 2)
        y = (dialog.winfo_screenheight() // 2) - (h // 2)
        dialog.geometry(f"{w}x{h}+{x}+{y}")
        dialog.after(100, lambda: dialog.grab_set())
        
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Заголовок
        color = "#00FF00" if is_bid else "#FF4444"
        ctk.CTkLabel(main_frame, text="📈 ПОКУПКА" if is_bid else "📉 ПРОДАЖА",
                     font=("Arial", 20, "bold"), text_color=color).pack(pady=(0, 10))
        
        # Поля ввода
        ctk.CTkLabel(main_frame, text="ID инструмента:", font=("Arial", 13), anchor="w").pack(fill="x", pady=(5, 0))
        tool_id_entry = ctk.CTkEntry(main_frame, height=32, font=("Arial", 13), placeholder_text="Введите ID инструмента")
        tool_id_entry.pack(fill="x", pady=(2, 5))
        
        # Количество и цена в одной строке
        row = ctk.CTkFrame(main_frame, fg_color="transparent")
        row.pack(fill="x", pady=5)
        
        for side, label, placeholder in [
            ("left", "Количество:", "Количество"),
            ("right", "Цена за единицу:", "Цена")
        ]:
            col = ctk.CTkFrame(row, fg_color="transparent")
            col.pack(side=side, fill="x", expand=True, padx=(0, 5) if side == "left" else (5, 0))
            ctk.CTkLabel(col, text=label, font=("Arial", 13), anchor="w").pack(fill="x")
            entry = ctk.CTkEntry(col, height=32, font=("Arial", 13), placeholder_text=placeholder)
            entry.pack(fill="x", pady=(2, 0))
            if side == "left":
                count_entry = entry
            else:
                price_entry = entry
        
        # Стоимость
        cost_frame = ctk.CTkFrame(main_frame, height=80)
        cost_frame.pack(fill="x", pady=8)
        cost_frame.pack_propagate(False)
        
        cost_label = ctk.CTkLabel(cost_frame, text="Введите количество и цену\nдля расчета стоимости",
                                  font=("Arial", 12), justify="left", text_color="gray")
        cost_label.pack(pady=8, padx=10, anchor="w")
        
        # Анонимность
        anonymous_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(main_frame, text="Анонимная заявка", variable=anonymous_var,
                        font=("Arial", 13), checkbox_width=22, checkbox_height=22).pack(pady=5)
        
        # Прогресс-бар
        progress_bar = ctk.CTkProgressBar(main_frame)
        progress_bar.pack(fill="x", pady=(0, 5))
        progress_bar.set(0)
        progress_bar.pack_forget()
        
        # Пересчет стоимости
        def recalculate(*args):
            try:
                count = float(count_entry.get() or "0")
                price = float(price_entry.get() or "0")
                if count > 0 and price > 0:
                    details = self.api.calculate_order_cost(count, price, is_bid)
                    total, comm, final = details['total_cost'], details['commission'], details['final_cost']
                    
                    text = f"Стоимость: {total:.4f} WMZ | Комиссия (0.05%): {comm:.4f} WMZ\n"
                    if is_bid:
                        text += f"К списанию: {final:.4f} WMZ"
                        if self.balance.available > 0:
                            rem = self.balance.available - final
                            text += f" | Останется: {rem:.4f} WMZ"
                            if rem < 0:
                                text += "\n⚠️ Недостаточно доступных средств!"
                    else:
                        text += f"К зачислению: {final:.4f} WMZ"
                    cost_label.configure(text=text, text_color="#00FF00" if final > 0 else "#FF4444")
                else:
                    cost_label.configure(text="Введите количество и цену для расчета стоимости", text_color="gray")
            except ValueError:
                cost_label.configure(text="Неверный формат данных", text_color="#FF4444")
        
        count_entry.bind("<KeyRelease>", recalculate)
        price_entry.bind("<KeyRelease>", recalculate)
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(5, 0))
        
        submit_btn = ctk.CTkButton(buttons_frame, text="📈 Купить" if is_bid else "📉 Продать",
                                   fg_color="#006400" if is_bid else "#8B0000",
                                   hover_color="#008000" if is_bid else "#A00000",
                                   height=38, font=("Arial", 14, "bold"))
        submit_btn.pack(pady=3, fill="x")
        
        cancel_btn = ctk.CTkButton(buttons_frame, text="Отмена", command=dialog.destroy,
                                   fg_color="#555555", hover_color="#666666",
                                   height=32, font=("Arial", 12))
        cancel_btn.pack(pady=3, fill="x")
        
        def submit():
            """Отправка ордера"""
            tool_id_str = tool_id_entry.get().strip()
            count_str = count_entry.get().strip()
            price_str = price_entry.get().strip()
            
            if not all([tool_id_str, count_str, price_str]):
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
            
            try:
                tool_id = int(tool_id_str)
                count = float(count_str)
                price = float(price_str)
                if tool_id <= 0 or count <= 0 or price <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат данных!")
                return
            
            details = self.api.calculate_order_cost(count, price, is_bid)
            final_cost = details['final_cost']
            
            if is_bid and final_cost > self.balance.available:
                if not messagebox.askyesno("⚠️ Недостаточно средств",
                                           f"Стоимость с комиссией: {final_cost:.4f} WMZ\n"
                                           f"Доступно: {self.balance.available:.4f} WMZ\n"
                                           f"Всего: {self.balance.total_wmz:.4f} WMZ\n\nПродолжить?"):
                    return
            
            submit_btn.configure(state="disabled", text="⏳ Отправка...")
            cancel_btn.configure(state="disabled")
            progress_bar.pack(fill="x", pady=(0, 5))
            progress_bar.start()
            
            def process():
                try:
                    response = self.api.offer_add(tool_id, count, is_bid, price, anonymous_var.get())
                    self.root.after(0, handle_result, response)
                except Exception as e:
                    self.root.after(0, handle_error, str(e))
            
            def handle_result(response):
                progress_bar.stop()
                progress_bar.pack_forget()
                
                if response.get('code') == 0:
                    offer_id = response.get('value', {}).get('OfferID', 'N/A')
                    
                    if is_bid:
                        self.balance.block_funds(final_cost)
                    self._refresh_balance_display()
                    
                    messagebox.showinfo("✅ Успех",
                                        f"Ордер создан!\n\n"
                                        f"Тип: {'Покупка' if is_bid else 'Продажа'}\n"
                                        f"ID: {tool_id}\n"
                                        f"Кол-во: {count:.4f}\n"
                                        f"Цена: {price:.4f} WMZ\n"
                                        f"Комиссия: {details['commission']:.4f} WMZ\n"
                                        f"Итого: {final_cost:.4f} WMZ\n"
                                        f"Offer ID: {offer_id}")
                    dialog.destroy()
                    self._refresh_orders()
                else:
                    messagebox.showerror("❌ Ошибка", f"Код: {response.get('code')}\n{response.get('desc')}")
                    submit_btn.configure(state="normal", text="📈 Купить" if is_bid else "📉 Продать")
                    cancel_btn.configure(state="normal")
            
            def handle_error(error_msg):
                progress_bar.stop()
                progress_bar.pack_forget()
                submit_btn.configure(state="normal", text="📈 Купить" if is_bid else "📉 Продать")
                cancel_btn.configure(state="normal")
                messagebox.showerror("❌ Ошибка", error_msg)
            
            self._run_async(process)
        
        submit_btn.configure(command=submit)
        tool_id_entry.focus()
    
    # ==================== Удаление ордера ====================
    
    def _delete_order(self):
        """Удаление выбранного ордера"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите ордер для удаления")
            return
        
        values = self.orders_tree.item(selection[0])['values']
        offer_id, order_type = values[0], values[3]
        
        try:
            order_cost = float(values[6])
        except (ValueError, IndexError):
            order_cost = 0.0
        
        if messagebox.askyesno("Подтверждение", f"Удалить ордер {offer_id}?"):
            def process():
                self.root.after(0, self._update_status, "Удаление ордера...")
                response = self.api.offer_delete(int(offer_id))
                self.root.after(0, self._handle_delete_result, response, order_type, order_cost)
                self.root.after(0, self._update_status, "Готов к работе")
            
            self._run_async(process)
    
    def _handle_delete_result(self, response, order_type, order_cost):
        """Обработка удаления ордера"""
        if response.get('code') == 0:
            if order_type == "Покупка" and order_cost > 0:
                self.balance.unblock_funds(order_cost)
            self._refresh_balance_display()
            messagebox.showinfo("Успех", "Ордер удален")
            self._refresh_orders()
        else:
            messagebox.showerror("Ошибка", response.get('desc', 'Unknown error'))
    
    def refresh_all(self):
        """Обновление всех данных"""
        self._refresh_balance()
        self._refresh_orders()
    
    def run(self):
        """Запуск GUI"""
        self.root.mainloop()