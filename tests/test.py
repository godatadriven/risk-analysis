import unittest
import random
from board import Board
from cards import Cards


class TestBoard(unittest.TestCase):

    def test_creation(self):
        for n_players, n_territories in [(3, 14), (4, 11), (5, 9), (6, 7)]:
            b = Board.create(n_players)
            self.assertEqual(b.n_territories(0), n_territories)

    def test_combat(self):
        b = Board.create(4)
        for _ in range(1000):
            self.assertIn(b.throw_dice(), (1, 2, 3, 4, 5, 6))
            n_att = random.randint(1, 10)
            n_def = random.randint(1, 10)
            att_loss, def_loss = b.fight(n_att, n_def)
            self.assertGreaterEqual(att_loss, 0)
            self.assertGreaterEqual(def_loss, 0)
            self.assertIn(att_loss + def_loss, (1, 2))
            self.assertLessEqual(att_loss, n_att)
            self.assertLessEqual(def_loss, n_def)

    def test_moves(self):
        random.seed(5)
        b = Board.create(3)
        self.assertEqual(b.continent_owner(4), 0)
        self.assertEqual(b.continent_owner(5), None)
        self.assertEqual(len(list(b.hostile_neighbors(4))), 3)
        self.assertEqual(len(list(b.friendly_neighbors(4))), 1)
        owner = b.owner(4)
        b.set_armies(4, 50)
        self.assertEqual(len(list(b.possible_attacks(owner))), 3)
        self.assertEqual(len(list(b.possible_fortifications(owner))), 1)
        self.assertTrue(b.attack(4, 37, 10))
        self.assertRaises(ValueError, b.attack, 37, 4, 14)
        b.fortify(4, 37, 10)
        self.assertRaises(ValueError, b.fortify, 37, 2, 14)

    def test_topology(self):
        b = Board.create(5)
        self.assertEqual(len(tuple(b.neighbors(0))), 5)

class TestCards(unittest.TestCase):

    def test_empty(self):
        c = Cards()
        self.assertEqual(c.total_cards, 0)
        self.assertEqual(len(c.complete_sets), 0)
        self.assertFalse(c.obligatory_turn_in)
        self.assertRaises(KeyError, c.is_complete, 'wrong_set')
        self.assertRaises(ValueError, c.turn_in, 'mix')

    def test_receive(self):
        c = Cards()
        c.receive()
        self.assertEqual(c.total_cards, 1)

    def test_full(self):
        c = Cards(3, 3, 3)
        self.assertEqual(c.total_cards, 9)
        self.assertTrue(c.obligatory_turn_in)
        self.assertEqual(len(c.complete_sets), 4)
        c.turn_in('cavalry')
        self.assertTrue(c.obligatory_turn_in)
        self.assertEqual(len(c.complete_sets), 2)
        c.turn_in('infantry')
        self.assertFalse(c.obligatory_turn_in)
        self.assertEqual(len(c.complete_sets), 1)
        c.turn_in('artillery')
        self.assertFalse(c.obligatory_turn_in)
        self.assertEqual(len(c.complete_sets), 0)

if __name__ == '__main__':
    unittest.main()
