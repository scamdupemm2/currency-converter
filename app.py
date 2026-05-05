import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

HISTORY_FILE = "data/history.json"

class CurrencyConverter:
    def __init__(self):
        self.rates_cache = {}

    def get_rates(self, base_currency: str = "USD") -> dict:
        try:
            url = f"https://open.er-api.com/v6/latest/{base_currency}"
            response = requests.get(url, timeout=10)
            data = response.json()
            if data.get("result") == "success":
                self.rates_cache = data["rates"]
                return self.rates_cache
            return {}
        except:
            return {}

    def convert(self, amount: float, from_currency: str, to_currency: str):
        if amount <= 0:
            return None
        rates = self.get_rates(from_currency)
        if not rates or to_currency not in rates:
            return None
        return round(amount * rates[to_currency], 2)

    def get_available_currencies(self) -> list:
        rates = self.get_rates("USD")
        if rates:
            return sorted(rates.keys())
        return ["USD", "EUR", "RUB", "GBP", "CNY", "JPY", "KZT"]

def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_conversion(from_curr: str, to_curr: str, amount: float, result: float):
    history = load_history()
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from": from_curr,
        "to": to_curr,
        "amount": amount,
        "result": result
    }
    history.append(entry)
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x500")
        self.converter = CurrencyConverter()

        self.setup_ui()
        self.load_currencies()

    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill="x")

        ttk.Label(frame, text="Сумма:").grid(row=0, column=0, sticky="w")
        self.amount_entry = ttk.Entry(frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Из:").grid(row=1, column=0, sticky="w", pady=5)
        self.from_combo = ttk.Combobox(frame, width=18, state="readonly")
        self.from_combo.grid(row=1, column=1, padx=5)

        ttk.Label(frame, text="В:").grid(row=2, column=0, sticky="w")
        self.to_combo = ttk.Combobox(frame, width=18, state="readonly")
        self.to_combo.grid(row=2, column=1, padx=5)

        ttk.Button(frame, text="Конвертировать", command=self.convert).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(frame, text="Очистить историю", command=self.clear_hist).grid(row=3, column=2, padx=10)

        ttk.Label(self.root, text="Результат:").pack(anchor="w", padx=10)
        self.result_label = ttk.Label(self.root, text="", font=("Arial", 14, "bold"))
        self.result_label.pack(padx=10, anchor="w")

        ttk.Label(self.root, text="История:").pack(anchor="w", padx=10, pady=(10, 0))
        self.tree = ttk.Treeview(self.root, columns=("date", "from", "to", "amount", "result"), show="headings", height=10)
        for col, text in [("date", "Дата"), ("from", "Из"), ("to", "В"), ("amount", "Сумма"), ("result", "Результат")]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.status = ttk.Label(self.root, text="Готов", relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")

    def load_currencies(self):
        currencies = self.converter.get_available_currencies()
        self.from_combo["values"] = currencies
        self.to_combo["values"] = currencies
        if currencies:
            self.from_combo.set("USD")
            self.to_combo.set("RUB")
        self.load_history_to_table()

    def convert(self):
        try:
            amount = float(self.amount_entry.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")
            return

        if amount <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть больше 0")
            return

        from_curr = self.from_combo.get()
        to_curr = self.to_combo.get()

        result = self.converter.convert(amount, from_curr, to_curr)
        if result is None:
            messagebox.showerror("Ошибка", "Не удалось получить курс. Проверьте интернет")
            return

        self.result_label.config(text=f"{amount} {from_curr} = {result} {to_curr}")
        save_conversion(from_curr, to_curr, amount, result)
        self.load_history_to_table()
        self.status.config(text=f"Конвертация выполнена: {result} {to_curr}")

    def load_history_to_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in load_history():
            self.tree.insert("", "end", values=(entry["date"], entry["from"], entry["to"], entry["amount"], entry["result"]))

    def clear_hist(self):
        clear_history()
        self.load_history_to_table()
        self.status.config(text="История очищена")

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()