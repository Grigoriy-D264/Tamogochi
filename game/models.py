"""Модуль с моделями"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Food:
    """Модель объекта еды"""

    name: str  # наименование
    satiety: int  # на сколько единиц утоляет голод
    price: int  # стоимость

    def __repr__(self) -> str:
        """Подготовить описание еды для вывода в консоль.

        Returns:
            Строка с названием, стоимостью и величиной насыщения.
        """
        return (
            f"{self.name} стоимость: {self.price}, "
            f"утоляет голод на {self.satiety} единиц"
        )


@dataclass
class Medicine:
    """Модель объекта лекарства"""

    name: str  # наименование
    price: int  # стоимость
    heal_hp: int  # сколько лечит HP
    number_of_uses: int  # максимальное количество применений
    uses: int = 0  # текущее количество применений

    def is_empty(self) -> bool:
        """Проверить, израсходованы ли все дозы лекарства.

        Returns:
            True при uses >= number_of_uses, иначе False.
        """
        return self.uses >= self.number_of_uses

    def __repr__(self) -> str:
        """Подготовить описание лекарства для вывода в консоль.

        Returns:
            Строка с названием, стоимостью, количеством восстанавливаемых HP
            и отношением оставшихся применений к их общему числу.
        """
        return (
            f"{self.name} стоимость: {self.price}, лечит на {self.heal_hp} HP, "
            f"использований: {self.number_of_uses - self.uses}/{self.number_of_uses}"
        )
