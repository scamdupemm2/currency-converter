import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import CurrencyConverter, load_history, save_conversion, clear_history, HISTORY_FILE

def test_convert_positive():
    conv = CurrencyConverter()
    result = conv.convert(100, "USD", "RUB")
    assert result is not None
    assert result > 0

def test_convert_negative_amount():
    conv = CurrencyConverter()
    result = conv.convert(-10, "USD", "RUB")
    assert result is None

def test_convert_zero():
    conv = CurrencyConverter()
    result = conv.convert(0, "USD", "RUB")
    assert result is None

def test_get_currencies():
    conv = CurrencyConverter()
    currs = conv.get_available_currencies()
    assert "USD" in currs
    assert "EUR" in currs
    assert "RUB" in currs

def test_save_and_load_history():
    clear_history()
    save_conversion("USD", "RUB", 100, 7500)
    history = load_history()
    assert len(history) == 1
    assert history[0]["from"] == "USD"
    assert history[0]["to"] == "RUB"
    clear_history()

def test_empty_history():
    clear_history()
    history = load_history()
    assert history == []