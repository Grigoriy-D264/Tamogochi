"""Точка входа и консольное меню игры «Тамагочи»."""

import os
import sys

from game.clicker import SimpleRandomClicker
from game.exceptions import EmptyInventory, NotEnoughMoney, TamagochiIsGone
from game.game import SimpleGame
from game.models import Food, Medicine
from game.tamagochi import SimpleTamagochi


def _clear_console() -> None:
    """Очистить экран только при интерактивном вводе и выводе.

    В Windows вызывается cls, в других системах — clear.
    Вывод, перенаправленный в файл или канал, не очищается.

    Returns:
        None.
    """
    if sys.stdin.isatty() and sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def main() -> None:
    """Создать компоненты игры и выполнять команды консольного меню.

    Цикл заканчивается при выборе выхода, смерти питомца или прерывании
    ввода. NotEnoughMoney и EmptyInventory выводятся как сообщения,
    TamagochiIsGone завершает игру. EOFError и KeyboardInterrupt
    обрабатываются с выводом прощания.

    Returns:
        None.
    """
    all_food = [
        Food(name="Бургер", satiety=20, price=40),
        Food(name="Салат", satiety=10, price=20),
        Food(name="Яблоко", satiety=10, price=15),
    ]
    all_medicine = [
        Medicine(name="Ибупрофен", price=30, heal_hp=20, number_of_uses=2),
    ]
    game = SimpleGame(
        SimpleTamagochi(),
        SimpleRandomClicker(10, 20),
        all_food,
        all_medicine,
    )
    print("Добро пожаловать в тамагочи-кликер!")
    output = ""

    try:
        while True:
            print(output)
            print(f"Сумка с едой: {game.food}")
            print(f"Сумка с лекарствами: {game.medicine}")
            status = game.get_status()
            print(
                f"\nСтатус: голод {status['hunger']}, здоровье {status['hp']}, "
                f"энергия {status['energy']}, монет {status['coins']}\n"
            )
            if game.tamagochi.is_sick():
                print("=======Тамагочи болеет======")
                print("=======Отдых действует менее эффективно=======")
            print(
                "1. Пойти на работу\n"
                "2. Купить еду\n"
                "3. Купить лекарство\n"
                "4. Покормить\n"
                "5. Вылечить\n"
                "6. Играть\n"
                "7. Отдых\n"
                "0. Выход"
            )
            try:
                output = ""
                match input("Выберите действие: ").strip():
                    case "1":
                        income = game.work()
                        output = f"Вы заработали {income} монет"
                    case "2":
                        game.buy_food()
                    case "3":
                        game.buy_medicine()
                    case "4":
                        game.feed_tamagochi()
                    case "5":
                        game.heal_tamagochi()
                    case "6":
                        game.play_with_tamagochi()
                        output = "Вы поиграли с питомцем"
                    case "7":
                        game.rest_tamagochi()
                        output = "Питомец отдохнул"
                    case "0":
                        print("До встречи!")
                        break
                    case _:
                        output = "Неверная команда"
            except (NotEnoughMoney, EmptyInventory) as error:
                output = str(error)
            _clear_console()
    except TamagochiIsGone as error:
        print(error)
    except (EOFError, KeyboardInterrupt):
        print("\nДо встречи!")


if __name__ == "__main__":
    main()
