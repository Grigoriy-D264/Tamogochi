"""Модуль с интерфейсом и реализацией кликера"""

import random
from abc import ABC, abstractmethod


class AbstractClicker(ABC):
    """Интерфейс для кликера"""

    @abstractmethod
    def __init__(self) -> None:
        """Задать контракт инициализации кликера.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def click(self) -> None:
        """Задать контракт обновления дохода за один клик.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def income_per_click(self) -> int:
        """Задать контракт доступа к доходу за клик.

        Returns:
            Количество монет за клик.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError


class SimpleRandomClicker(AbstractClicker):
    """Кликер со случайным целочисленным доходом в заданном диапазоне."""

    def __init__(self, min_income: int = 10, max_income: int = 20) -> None:
        """Настроить границы дохода.

        Args:
            min_income: Минимальный доход включительно.
            max_income: Максимальный доход включительно.

        Returns:
            None.

        Raises:
            ValueError: Границы нецелые, отрицательные или перепутаны.
        """
        if (
            type(min_income) is not int
            or type(max_income) is not int
            or min_income < 0
            or max_income < min_income
        ):
            raise ValueError("Доход задаётся целыми числами: 0 ≤ минимум ≤ максимум")
        self._min_income = min_income
        self._max_income = max_income
        self._income_per_click = min_income

    def click(self) -> None:
        """Выбрать и сохранить случайный доход в настроенных границах.

        Returns:
            None.
        """
        self._income_per_click = random.randint(self._min_income, self._max_income)

    @property
    def income_per_click(self) -> int:
        """Получить сохранённый доход без нового клика.

        Returns:
            Доход последнего клика; до первого клика — min_income.
        """
        return self._income_per_click
