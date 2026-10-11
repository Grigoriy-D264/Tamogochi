"""Модуль с интерфейсом и реализацией класса игры"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import replace
from typing import Any

from .clicker import AbstractClicker
from .exceptions import EmptyInventory, NotEnoughMoney, TamagochiIsGone
from .models import Food, Medicine
from .tamagochi import AbstractTamagochi


class AbstractGame(ABC):
    """Интерфейс для логики игры"""

    @abstractmethod
    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Задать контракт инициализации игры.

        Args:
            tamagochi: Питомец, реализующий AbstractTamagochi.
            clicker: Кликер, реализующий AbstractClicker.
            all_food: Каталог доступной для покупки еды.
            all_medicine: Каталог доступных для покупки лекарств.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def work(self) -> int:
        """Задать контракт заработка монет за действие работы.

        Returns:
            Количество заработанных монет.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def buy_food(self) -> None:
        """Задать контракт покупки еды.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def buy_medicine(self) -> None:
        """Задать контракт покупки лекарства.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def feed_tamagochi(self) -> None:
        """Задать контракт кормления питомца едой из сумки.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def heal_tamagochi(self) -> None:
        """Задать контракт лечения питомца лекарством из сумки.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def rest_tamagochi(self) -> None:
        """Задать контракт отдыха питомца в рамках игрового хода.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def play_with_tamagochi(self) -> None:
        """Задать контракт игры с питомцем в рамках игрового хода.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """Задать контракт получения состояния игры.

        Returns:
            Словарь характеристик питомца и количества монет.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def food(self) -> list[Food]:
        """Задать контракт доступа к сумке с едой.

        Returns:
            Список купленных порций еды.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def medicine(self) -> list[Medicine]:
        """Задать контракт доступа к сумке с лекарствами.

        Returns:
            Список купленных лекарств.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError


class SimpleGame(AbstractGame):
    """Игра управляет монетами, сумками и последовательностью действий."""

    def __init__(
        self,
        tamagochi: AbstractTamagochi,
        clicker: AbstractClicker,
        all_food: list[Food],
        all_medicine: list[Medicine],
    ) -> None:
        """Связать компоненты и создать пустые сумки и кошелёк.

        Args:
            tamagochi: Питомец, реализующий абстрактный интерфейс.
            clicker: Кликер, выдающий доход за действие работы.
            all_food: Каталог доступной еды.
            all_medicine: Каталог доступных лекарств.

        Returns:
            None.
        """
        self.tamagochi = tamagochi
        self._clicker = clicker
        self._all_food = list(all_food)
        self._all_medicine = list(all_medicine)
        self._food: list[Food] = []
        self._medicine: list[Medicine] = []
        self._coins = 0

    def _ensure_alive(self) -> None:
        """Проверить жизнь питомца перед выполнением действия.

        Returns:
            None.

        Raises:
            TamagochiIsGone: Питомец уже погиб.
        """
        if not self.tamagochi.is_alive():
            raise TamagochiIsGone("Питомец погиб. Игра окончена.")

    @staticmethod
    def _choose(items: Sequence[Food | Medicine]) -> int | None:
        """Запросить номер предмета с повтором при ошибке ввода.

        Args:
            items: Каталог или содержимое сумки.

        Returns:
            Индекс выбранного предмета или None при отмене/пустом списке.

        Raises:
            EOFError: Ввод закрыт.
            KeyboardInterrupt: Пользователь прервал ввод.
        """
        if not items:
            print("Список предметов пуст.")
            return None
        for number, item in enumerate(items, start=1):
            print(f"{number}. {item}")
        print("0. Отмена")
        while True:
            try:
                number = int(input("Выберите предмет: "))
            except ValueError:
                print("Введите целый номер предмета или 0 для отмены.")
                continue
            if number == 0:
                return None
            if 1 <= number <= len(items):
                return number - 1
            print("Такого номера нет. Повторите выбор.")

    def work(self) -> int:
        """Заработать монеты одним кликом и обновить питомца.

        Returns:
            Количество заработанных монет.

        Raises:
            TamagochiIsGone: Питомец погиб до или после работы.
        """
        self._ensure_alive()
        self._clicker.click()
        income = self._clicker.income_per_click
        self._coins += income
        self.tamagochi.update()
        return income

    def _pay(self, price: int) -> None:
        """Списать стоимость предмета из кошелька.

        Args:
            price: Стоимость выбранного предмета в монетах.

        Returns:
            None.

        Raises:
            NotEnoughMoney: Монет недостаточно; содержимое кошелька не меняется.
        """
        if self._coins < price:
            raise NotEnoughMoney(
                f"Недостаточно монет: нужно {price}, есть {self._coins}."
            )
        self._coins -= price

    def buy_food(self) -> None:
        """Выбрать и купить порцию еды; отмена не расходует ход.

        Returns:
            None.

        Raises:
            NotEnoughMoney: Покупка недоступна по цене.
            TamagochiIsGone: Питомец погиб до или после действия.
            EOFError: Ввод закрыт.
            KeyboardInterrupt: Пользователь прервал ввод.
        """
        self._ensure_alive()
        index = self._choose(self._all_food)
        if index is None:
            return
        food = self._all_food[index]
        self._pay(food.price)
        self._food.append(food)
        self.tamagochi.update()

    def buy_medicine(self) -> None:
        """Купить отдельный экземпляр лекарства с неиспользованными дозами.

        Returns:
            None.

        Raises:
            NotEnoughMoney: Покупка недоступна по цене.
            TamagochiIsGone: Питомец погиб до или после действия.
            EOFError: Ввод закрыт.
            KeyboardInterrupt: Пользователь прервал ввод.
        """
        self._ensure_alive()
        index = self._choose(self._all_medicine)
        if index is None:
            return
        medicine = replace(self._all_medicine[index], uses=0)
        self._pay(medicine.price)
        self._medicine.append(medicine)
        self.tamagochi.update()

    def feed_tamagochi(self) -> None:
        """Выбрать порцию из сумки, накормить питомца и расходовать еду.

        Returns:
            None.

        Raises:
            EmptyInventory: Сумка с едой пуста.
            TamagochiIsGone: Питомец погиб до или после действия.
            EOFError: Ввод закрыт.
            KeyboardInterrupt: Пользователь прервал ввод.
        """
        self._ensure_alive()
        if not self._food:
            raise EmptyInventory("Сумка с едой пуста. Сначала купите еду.")
        index = self._choose(self._food)
        if index is None:
            return
        self.tamagochi.feed(self._food[index])
        self._food.pop(index)
        self.tamagochi.update()

    def heal_tamagochi(self) -> None:
        """Применить выбранное лекарство; удалить его после последней дозы.

        Returns:
            None.

        Raises:
            EmptyInventory: Сумка пуста или дозы выбранного лекарства закончились.
            TamagochiIsGone: Питомец погиб до или после действия.
            EOFError: Ввод закрыт.
            KeyboardInterrupt: Пользователь прервал ввод.
        """
        self._ensure_alive()
        if not self._medicine:
            raise EmptyInventory("Сумка с лекарствами пуста. Сначала купите лекарство.")
        index = self._choose(self._medicine)
        if index is None:
            return
        medicine = self._medicine[index]
        self.tamagochi.heal(medicine)
        if medicine.is_empty():
            self._medicine.pop(index)
        self.tamagochi.update()

    def rest_tamagochi(self) -> None:
        """Уложить питомца отдыхать и обновить состояние за один ход.

        Returns:
            None.

        Raises:
            TamagochiIsGone: Питомец погиб до или после действия.
        """
        self._ensure_alive()
        self.tamagochi.rest()
        self.tamagochi.update()

    def play_with_tamagochi(self) -> None:
        """Поиграть с питомцем и обновить состояние за один ход.

        Returns:
            None.

        Raises:
            TamagochiIsGone: Питомец погиб до или после действия.
        """
        self._ensure_alive()
        self.tamagochi.play()
        self.tamagochi.update()

    def get_status(self) -> dict[str, int]:
        """Получить состояние игры без расходования хода.

        Returns:
            Новый словарь с ключами hunger, fatigue, hp, energy и coins.
            Изменение словаря не влияет на состояние игры.
        """
        return {**self.tamagochi.status, "coins": self._coins}

    @property
    def food(self) -> list[Food]:
        """Получить содержимое сумки с едой.

        Returns:
            Копия списка купленных порций. Объекты Food неизменяемы;
            изменение самого списка не влияет на сумку.
        """
        return list(self._food)

    @property
    def medicine(self) -> list[Medicine]:
        """Получить содержимое сумки с лекарствами.

        Returns:
            Копия списка купленных лекарств с текущими счётчиками доз.
            Элементы — те же объекты Medicine, а не их независимые копии.
        """
        return list(self._medicine)
