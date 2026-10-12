"""Regression checks for the failures reported by the submission checker."""

import importlib
import inspect
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from game.clicker import SimpleRandomClicker
from game.exceptions import NotEnoughMoney, TamagochiIsGone
from game.game import SimpleGame
from game.models import Food, Medicine
from game.tamagochi import SimpleTamagochi
from main import main


class SubmissionChecks(unittest.TestCase):
    def setUp(self):
        self.random = patch("game.tamagochi.random.random", return_value=1.0)
        self.random.start()
        self.addCleanup(self.random.stop)
        self.pet = SimpleTamagochi()
        self.clicker = SimpleRandomClicker(10, 10)
        self.food = Food("Apple", 20, 10)
        self.medicine = Medicine("Medicine", 10, 20, 2)
        self.game = SimpleGame(
            self.pet, self.clicker, [self.food], [self.medicine]
        )

    def choose(self, action, value="1"):
        with patch("builtins.input", return_value=value), redirect_stdout(io.StringIO()):
            action()

    def test_concrete_classes_discoverable_in_each_module(self):
        for module_name, abstract_name in (
            ("clicker", "AbstractClicker"),
            ("tamagochi", "AbstractTamagochi"),
            ("game", "AbstractGame"),
        ):
            with self.subTest(module=module_name):
                module = importlib.import_module(f"game.{module_name}")
                abstract = getattr(module, abstract_name)
                concrete = [
                    cls for _, cls in inspect.getmembers(module, inspect.isclass)
                    if cls is not abstract and issubclass(cls, abstract)
                    and cls.__module__ == module.__name__
                    and not inspect.isabstract(cls)
                ]
                self.assertTrue(concrete)

    def test_main_exits_on_zero(self):
        with patch("builtins.input", return_value="0") as input_mock:
            with redirect_stdout(io.StringIO()):
                self.assertIsNone(main())
        input_mock.assert_called_once()

    def test_game_status(self):
        self.assertEqual(self.game.get_status(), {
            "hunger": 0, "fatigue": 0, "hp": 100, "energy": 100, "coins": 0,
        })

    def test_feed_reduces_hunger(self):
        for _ in range(5):
            self.pet.update()
        before = self.pet.status["hunger"]
        self.pet.feed(self.food)
        self.assertEqual(self.pet.status["hunger"], before - self.food.satiety)

    def test_rest_restores_energy(self):
        self.pet.play()
        before = self.pet.status["energy"]
        self.pet.rest()
        self.assertGreater(self.pet.status["energy"], before)

    def test_heal_restores_hp_and_consumes_one_dose(self):
        for _ in range(18):
            self.pet.update()
        before = self.pet.status["hp"]
        self.pet.heal(self.medicine)
        self.assertEqual(self.pet.status["hp"], before + self.medicine.heal_hp)
        self.assertEqual(self.medicine.uses, 1)

    def test_play_changes_state(self):
        before = self.pet.status
        self.pet.play()
        self.assertLess(self.pet.status["energy"], before["energy"])
        self.assertGreater(self.pet.status["fatigue"], before["fatigue"])

    def test_update_changes_state(self):
        before = self.pet.status
        self.pet.update()
        self.assertGreater(self.pet.status["hunger"], before["hunger"])

    def test_work_earns_income_and_clicks_once(self):
        with patch.object(self.clicker, "click", wraps=self.clicker.click) as click:
            self.assertEqual(self.game.work(), 10)
        click.assert_called_once()
        self.assertEqual(self.game.get_status()["coins"], 10)
        self.assertEqual(self.pet.status["hunger"], 5)

    def test_buy_food_and_feed_consumes_selected_item(self):
        self.game.work()
        self.choose(self.game.buy_food)
        self.assertEqual(self.game.food, [self.food])
        self.assertEqual(self.game.get_status()["coins"], 0)
        self.choose(self.game.feed_tamagochi)
        self.assertEqual(self.game.food, [])
        self.assertEqual(self.pet.status["hunger"], 5)

    def test_medicine_purchases_have_independent_doses(self):
        self.game.work()
        self.game.work()
        self.choose(self.game.buy_medicine)
        self.choose(self.game.buy_medicine)
        first, second = self.game.medicine
        self.assertIsNot(first, second)
        self.choose(self.game.heal_tamagochi)
        self.assertEqual((first.uses, second.uses, self.medicine.uses), (1, 0, 0))
        self.choose(self.game.heal_tamagochi)
        self.assertEqual(self.game.medicine, [second])

    def test_cancel_and_insufficient_money_preserve_state(self):
        before = self.game.get_status()
        self.choose(self.game.buy_food, "0")
        self.assertEqual(self.game.get_status(), before)
        with self.assertRaises(NotEnoughMoney):
            self.choose(self.game.buy_food)
        self.assertEqual(self.game.get_status(), before)
        self.assertEqual(self.game.food, [])

    def test_game_end_reachable_and_blocks_further_actions(self):
        with self.assertRaises(TamagochiIsGone):
            for _ in range(100):
                self.game.work()
        self.assertFalse(self.pet.is_alive())
        coins = self.game.get_status()["coins"]
        with self.assertRaises(TamagochiIsGone):
            self.game.work()
        self.assertEqual(self.game.get_status()["coins"], coins)


if __name__ == "__main__":
    unittest.main()
