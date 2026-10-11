"""Модуль с исключениями"""


class TamagochiIsGone(Exception):
    """Ошибка при смерти тамагочи"""


class NotEnoughMoney(Exception):
    """Ошибка когда не хватает монет для покупки"""


class EmptyInventory(Exception):
    """Для действия нет предмета или лекарство уже использовано до конца."""
