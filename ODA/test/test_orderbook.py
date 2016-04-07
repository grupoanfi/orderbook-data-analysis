import unittest
from ODA.market_cols import OrderKeys, ExecutionResponse, SharedValues
from utils import *
import random
from ODA.market import Market, Request, Order
from ODA.orderBook import Level, orders2levels
import ODA.check_order as checker

__author__ = 'Math'

global_market_type = LobsterKeys.clean_price

req_ask1 = {
    OrderKeys.size: 1000,
    OrderKeys.direction: -1,
    OrderKeys.price: 1600,
    OrderKeys.id_user: 'juanqui',
    OrderKeys.group: 'Bancolombia',
    OrderKeys.event: 1,
    OrderKeys.id_order: 1,
}

req_ask2 = {
    OrderKeys.size: 1000,
    OrderKeys.direction: -1,
    OrderKeys.price: 1500,
    OrderKeys.id_user: 'juanqui',
    OrderKeys.group: 'Bancolombia',
    OrderKeys.event: 1,
    OrderKeys.id_order: 2
}

req_bid1 = {
    OrderKeys.size: 1000,
    OrderKeys.direction: 1,
    OrderKeys.price: 1400,
    OrderKeys.id_user: 'juanqui',
    OrderKeys.group: 'Bancolombia',
    OrderKeys.event: 1,
    OrderKeys.id_order: 3
}

req_bid2 = {
    OrderKeys.size: 1000,
    OrderKeys.direction: 1,
    OrderKeys.price: 1300,
    OrderKeys.id_user: 'juanqui',
    OrderKeys.group: 'Bancolombia',
    OrderKeys.event: 1,
    OrderKeys.id_order: 4
}


class TestsLevel(unittest.TestCase):
    def setUp(self):
        self.my_mini_market = Market()
        self.my_ordens = Generear_ordenes_limit()

    def tearDown(self):
        pass

    def test_levels_overload_less_than_or_equal(self):
        """
        This tests checks if the levels in bid direction overloading of <= is
        correct. It Creates a random number of cases, for every case,
        generates two prices, after that, it instances two levels with those prices
        and check if the levels <= is the same of the raw prices
        :return:
        """

        num_prices = random.randint(10, 50)
        market_type = SharedValues.market_type

        for i in xrange(num_prices):
            direction = random.choice(LobsterKeys.directions)

            p1 = random.uniform(10, 5000)
            p2 = random.uniform(10, 5000)

            if market_type == LobsterKeys.clean_price:
                if direction == LobsterKeys.ask:
                    res = p1 <= p2
                else:
                    res = p1 >= p2
            else:
                if direction == LobsterKeys.ask:
                    res = p1 >= p2
                else:
                    res = p1 <= p2

            l1 = Level(direction, p1, list())
            l2 = Level(direction, p2, list())

            test_res = l1 <= l2
            self.assertEqual(test_res, res,
                             msg="Inequality failed between levels\n {0} and {1}"
                                 " should be: {2} and is {3}. The direction is {4}"
                             .format(l1, l2, res, test_res, direction))

    def test_levels_overload_less_than_strict(self):
        """
        This tests checks if the levels in bid direction overloading of < is
        correct. It Creates a random number of cases, for every case,
        generates two prices, after that, it instances two levels with those prices
        and check if the levels < is the same of the raw prices
        :return:
        """

        num_prices = random.randint(10, 50)
        market_type = SharedValues.market_type

        for i in xrange(num_prices):
            direction = random.choice(LobsterKeys.directions)

            p1 = random.uniform(10, 5000)
            p2 = random.uniform(10, 5000)

            if market_type == LobsterKeys.clean_price:
                if direction == LobsterKeys.ask:
                    res = p1 <= p2
                else:
                    res = p1 >= p2
            else:
                if direction == LobsterKeys.ask:
                    res = p1 >= p2
                else:
                    res = p1 <= p2

            l1 = Level(direction, p1, list())
            l2 = Level(direction, p2, list())

            test_res = l1 < l2
            self.assertEqual(test_res, res,
                             msg="Inequality failed between levels\n {0} and {1}"
                                 " should be: {2} and is {3}. The direction is {4}"
                             .format(l1, l2, res, test_res, direction))

    def test_orders2levels(self):
        """
        This tests checks the function named orders2levels in orderBook.py,
        basically this test generates a number of random requests with event = 1
        (ie aggregations), the check if the order in the levels list math
        the correct order in both directions

        :return:
        """
        # TODO: modify the test to support dirty_price
        num_levels = random.randint(1, 100)

        range_lvl_ask = range(1, num_levels)
        range_lvl_bid = list(reversed(range(1, num_levels)))

        orders_bid = [Order(**gen_request_limit_bid(p, 10, id_order=p))
                      for p in range_lvl_bid]
        orders_ask = [Order(**gen_request_limit_ask(p, 10, id_order=p))
                      for p in range_lvl_ask]

        my_snapshot = {LobsterKeys.bid: orders_bid, LobsterKeys.ask: orders_ask}

        my_levels = {LobsterKeys.bid: [Level(LobsterKeys.bid, order.price, [order])
                                       for order in orders_bid],
                     LobsterKeys.ask: [Level(LobsterKeys.bid, order.price, [order])
                                       for order in orders_ask]}

        function_levels = orders2levels(my_snapshot)

        self.assertDictEqual(my_levels, function_levels,
                             msg="the levels formed by the test {0} "
                                 "and the formed by the function: {1} not match".
                             format(my_levels, function_levels))



