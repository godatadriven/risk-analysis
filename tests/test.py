import random
import unittest

import definitions
from board import Board, Territory
from cards import Cards
from game import Game
from genome import Gene, ListGene, Genome
from missions import missions
from player import Player, RandomPlayer
from ranker import TrueskillRanker, RiskRanker


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


class TestDefinitions(unittest.TestCase):

    def test_territories(self):
        for i in range(42):
            self.assertEqual(type(definitions.territory_names[i]), str)
            self.assertIn(i, definitions.territory_continents.keys())

    def test_neighbors(self):
        for i in range(42):
            neighbors = definitions.territory_neighbors[i]
            for neighbor in neighbors:
                self.assertIn(i, definitions.territory_neighbors[neighbor])


class TestGame(unittest.TestCase):

    def test_play(self):
        random.seed(0)
        for i in [3, 4, 5, 6]:
            players = [Player() for _ in range(i)]
            g = Game.create(players)
            g.initialize_armies()
            for _ in range(1000):
                g.play_turn()

    def test_play_random(self):
        random.seed(0)
        for i in [3, 4, 5, 6]:
            players = [RandomPlayer() for _ in range(i)]
            g = Game.create(players)
            g.initialize_armies()
            while not g.has_ended():
                g.play_turn()


class TestGenome(unittest.TestCase):

    def test_gene(self):
        a = Gene(name='x', min_value=-1., max_value=1., volatility=0.5, granularity=0.1, precision=2)
        for i in range(1000):
            v = a.initialize()
            self.assertGreaterEqual(v, -1.)
            self.assertLessEqual(v, 1.)
            v = a.mutate(v)
            self.assertGreaterEqual(v, -1.)
            self.assertLessEqual(v, 1.)
        b = ListGene(name='y', values=[0, 1, 2], volatility=0.5)
        for i in range(1000):
            v = b.initialize()
            self.assertIn(v, [0, 1, 2])
            v = b.mutate(v)
            self.assertIn(v, [0, 1, 2])

    def test_genome(self):
        Genome.specifications = [
            Gene('x', -1, 1, 0.5, 0.1, 2),
            Gene('y', -1, 1, 0.5, 0.1, 2),
            ListGene('z', [3, 4], 0.5)
        ]
        g1 = Genome.create()
        g2 = Genome.create()
        g3 = g1.combine(g2)
        _ = g3.mutate()


class TestMission(unittest.TestCase):

    def test_evaluate(self):
        b = Board(list(Territory(i, 0, 2) for i in range(42)))
        all_missions = missions(2)
        for m in all_missions:
            m.assign_to(0)
            self.assertTrue(m.evaluate(b))
            m.assign_to(1)
            self.assertFalse(m.evaluate(b))


class TestRanker(unittest.TestCase):

    def test_tsrank(self):
        tsr = TrueskillRanker()
        self.assertEqual(tsr.score(0), 0)
        tsr.update([0], [1, 2])
        self.assertEqual(tsr.score(1), tsr.score(2))
        self.assertGreater(tsr.score(0), tsr.score(1))
        tsr.update([0], [1, 2])
        tsr.update([1], [0, 2])
        self.assertEqual([i for i, _ in tsr.rank()], [0, 1, 2])

    def test_riskrank(self):
        for n_players in [2, 3, 4, 5, 6]:
            rr = RiskRanker([RandomPlayer() for _ in range(20)], n_players=n_players)
            rr.run(1)
            rank = rr.rank()
            self.assertEqual(len(rank), 20)

if __name__ == '__main__':
    unittest.main()
