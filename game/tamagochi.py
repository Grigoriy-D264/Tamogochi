"""Модуль с интерфейсом и реализациями класса тамагочи"""

import random
from abc import ABC, abstractmethod

from .exceptions import EmptyInventory, TamagochiIsGone
from .models import Food, Medicine


class AbstractTamagochi(ABC):
    """Интерфейс логики тамагочи"""

    @abstractmethod
    def feed(self, food: Food) -> None:
        """Задать контракт кормления питомца.

        Args:
            food: Порция еды для кормления.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def play(self) -> None:
        """Задать контракт игры с питомцем.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def rest(self) -> None:
        """Задать контракт отдыха питомца.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def heal(self, medicine: Medicine) -> None:
        """Задать контракт лечения питомца.

        Args:
            medicine: Лекарство для лечения.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def status(self) -> dict[str, int]:
        """Задать контракт доступа к характеристикам питомца.

        Returns:
            Словарь характеристик питомца с целочисленными значениями.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def is_alive(self) -> bool:
        """Задать контракт проверки жизни питомца.

        Returns:
            True, если питомец жив, иначе False.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def is_sick(self) -> bool:
        """Задать контракт проверки болезни питомца.

        Returns:
            True, если питомец болен, иначе False.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self) -> None:
        """Задать контракт обновления питомца после успешного действия.

        Returns:
            None.

        Raises:
            NotImplementedError: Вызван абстрактный метод без реализации.
        """
        raise NotImplementedError


class SimpleTamagochi(AbstractTamagochi):
    """Питомец с голодом, усталостью, энергией, здоровьем и болезнью."""

    def __init__(self) -> None:
        """Создать здорового и отдохнувшего питомца.

        Голод и усталость равны 0, здоровье и энергия — 100. Болезни нет.

        Returns:
            None.
        """
        self._hunger = 0
        self._fatigue = 0
        self._hp = 100
        self._energy = 100
        self._sick = False
        self._compensate_healing_tick = False

    def _ensure_alive(self) -> None:
        """Проверить, что питомец жив.

        Returns:
            None.

        Raises:
            TamagochiIsGone: Питомец уже погиб.
        """
        if not self.is_alive():
            raise TamagochiIsGone("Питомец погиб. Игра окончена.")

    def feed(self, food: Food) -> None:
        """Уменьшить голод на насыщение еды, сохраняя диапазон 0–100.

        Args:
            food: Порция еды; satiety задаёт величину насыщения.

        Returns:
            None.

        Raises:
            TamagochiIsGone: Питомец уже погиб.
        """
        self._ensure_alive()
        self._hunger = max(0, min(100, self._hunger - food.satiety))

    def play(self) -> None:
        """Потратить 10 энергии и добавить 10 усталости.

        Returns:
            None.

        Raises:
            TamagochiIsGone: Питомец уже погиб.
        """
        self._ensure_alive()
        self._energy = max(0, self._energy - 10)
        self._fatigue = min(100, self._fatigue + 10)

    def rest(self) -> None:
        """Восстановить энергию и снять усталость на 30 (при болезни 15).

        Returns:
            None.

        Raises:
            TamagochiIsGone: Питомец уже погиб.
        """
        self._ensure_alive()
        recovery = 15 if self.is_sick() else 30
        self._energy = min(100, self._energy + recovery)
        self._fatigue = max(0, self._fatigue - recovery)

    def heal(self, medicine: Medicine) -> None:
        """Вылечить болезнь и восстановить здоровье одной дозой medicine.

        Урон ближайшего update компенсируется, чтобы итоговый прирост HP
        соответствовал heal_hp (с ограничением максимального здоровья).

        Args:
            medicine: Лекарство с оставшимися применениями.

        Returns:
            None.

        Raises:
            TamagochiIsGone: Питомец уже погиб.
            EmptyInventory: Лекарство закончилось.
        """
        self._ensure_alive()
        if medicine.is_empty():
            raise EmptyInventory("Лекарство закончилось.")
        self._hp = min(100, self._hp + medicine.heal_hp)
        self._sick = False
        medicine.uses += 1
        self._compensate_healing_tick = True

    @property
    def status(self) -> dict[str, int]:
        """Получить текущие характеристики без изменения состояния.

        Returns:
            Новый словарь с ключами hunger, fatigue, hp и energy.
            Изменение словаря не влияет на питомца.
        """
        return {
            "hunger": self._hunger,
            "fatigue": self._fatigue,
            "hp": self._hp,
            "energy": self._energy,
        }

    def is_alive(self) -> bool:
        """Проверить здоровье питомца.

        Returns:
            True при hp >= 0 (включая нулевое здоровье), иначе False.
        """
        return self._hp >= 0

    def is_sick(self) -> bool:
        """Проверить текущее наличие болезни.

        Returns:
            True, если питомец болен, иначе False.
        """
        return self._sick

    def update(self) -> None:
        """Обновить потребности, болезнь и здоровье за один ход.

        Returns:
            None.

        Raises:
            TamagochiIsGone: Питомец погиб до или во время обновления.
        """
        self._ensure_alive()
        self._hunger = min(100, self._hunger + 5)
        self._fatigue = min(100, self._fatigue + 5)
        self._energy = max(0, self._energy - 5)
        if not self._sick and random.random() < 0.1:
            self._sick = True
        damage = 0
        if self._hunger >= 80 or self._fatigue >= 80:
            damage += 10
        if self._sick:
            damage += 5
            self._fatigue = min(100, self._fatigue + 5)
        self._hp -= damage
        if self._compensate_healing_tick:
            self._hp += damage
        self._compensate_healing_tick = False
        self._ensure_alive()
