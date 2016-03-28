__author__ = 'Math'

import unittest
from ODA.market_cols import OrderKeys, ExecutionResponse
from utils import Generear_ordenes_limit
import random
import pandas as pd
from ODA.market import Market, Request


class TestMiniMArket(unittest.TestCase):
    def setUp(self):
        self.my_mini_market = Market(1)
        self.my_ordens = Generear_ordenes_limit()

    def tearDown(self):
        # df = pd.DataFrame(self.my_mini_market.e)
        # #print self.my_mini_market.executed_reqs
        # print df
        # #print self.my_mini_market.orders_queue
        pass


    def test_order_ask(self):

        n_orders = random.randint(1, 20)

        l_res = []
        self.my_ordens.agregar_ordenes_ask(n_orders)

        for order in self.my_ordens.list_ordenes_ask:
            l_res.append(self.my_mini_market.execute_request(Request(**order)).msg)

        self.assertSetEqual(set(l_res), {ExecutionResponse.OK})

        l = []

        for index in range(n_orders):
            for order in self.my_mini_market.orders_queue[-1]:
                if order.id_order == index:
                    l.append(index)

        self.assertEqual(l, range(n_orders))


    def test_order_bid(self):

        n_orders = random.randint(1, 1000)

        l_res = []
        self.my_ordens.agregar_ordenes_bid(n_orders)

        for order in self.my_ordens.list_ordenes_bid:
            l_res.append(self.my_mini_market.execute_request(Request(**order)).msg)

        self.assertSetEqual(set(l_res), {ExecutionResponse.OK})

        l = []

        for index in range(n_orders):
            for order in self.my_mini_market.orders_queue[1]:
                if order.id_order == index:
                    l.append(index)

        self.assertEqual(l, range(n_orders))

    def test_order_limists(self):
        self.my_mini_market.conserv_id = False

        n_orders = random.randint(1, 1000)

        n_ordenes_descartadas = random.choice(
            [0, random.randint(1, n_orders - 1)])

        self.my_ordens.generar_ordenes_resord(n_orders, cero=(-1) * (
            n_ordenes_descartadas - 1))

        order_list = self.my_ordens.list_total_ordenes()

        l_res = []

        for order in order_list:
            res = self.my_mini_market.execute_request(Request(**order))
            l_res.append(res.msg)


        invalid = l_res.count(ExecutionResponse.LIMITPRICEINVALID)

        self.assertEqual(invalid, n_ordenes_descartadas)

        l = []

        orders_in_market = self.my_mini_market.orders_queue[1][:]
        orders_in_market.extend(self.my_mini_market.orders_queue[-1])

        orders_activ = len(self.my_mini_market.orders_queue[-1]) + len(
            self.my_mini_market.orders_queue[1])

        for index in range(orders_activ):
            for order in orders_in_market:
                if order.id_order == index:
                    l.append(index)

        self.assertEqual(l, range(orders_activ))

    def test_modification_order(self):
        n_orders = random.randint(1, 1000)

        n_ordenes_descartadas = 0

        self.my_ordens.generar_ordenes_resord(n_orders, cero=(-1) * (
            n_ordenes_descartadas - 1))

        order_list = self.my_ordens.list_total_ordenes()

        for order in order_list:
            self.my_mini_market.execute_request(Request(**order))

        random_direction = random.choice([-1, 1])

        random_order = random.choice(
            self.my_mini_market.orders_queue[random_direction])

        old_vol = random_order.size

        random_exedent = random.randint(0, old_vol)

        d = random.choice([-1, 1])

        random_vol = random_order.size + random_exedent * d

        new_order = random_order.to_dict().copy()

        new_order[OrderKeys.size] = random_vol

        new_order[OrderKeys.event] = 2

        res = self.my_mini_market.execute_request(Request(**new_order))

        if res == ExecutionResponse.OK:
            index = self.my_mini_market.orders_queue[random_direction].index(
                random_order)

            order = self.my_mini_market.orders_queue[random_direction][index]

            self.assertEqual(order.size, random_vol)

    def test_cancelation_order(self):
        n_orders = random.randint(1, 1000)

        n_ordenes_descartadas = 0

        self.my_ordens.generar_ordenes_resord(n_orders, cero=(-1) * (
            n_ordenes_descartadas - 1))

        order_list = self.my_ordens.list_total_ordenes()

        for order in order_list:
            self.my_mini_market.execute_request(Request(**order))

        random_direction = random.choice([-1, 1])

        random_order = random.choice(
            self.my_mini_market.orders_queue[random_direction])

        new_order = random_order.to_dict().copy()

        new_order[OrderKeys.event] = 3

        len_before = len(self.my_mini_market.orders_queue[random_direction])

        self.my_mini_market.execute_request(Request(**new_order))

        len_after = len(self.my_mini_market.orders_queue[random_direction])

        self.assertEqual(len_after, len_before - 1)

        self.assertRaises(ValueError, self.my_mini_market.orders_queue[
            random_direction].index, random_order)

    def test_market_order(self):
        n_orders = random.randint(1, 10)

        n_ordenes_descartadas = 0

        self.my_ordens.generar_ordenes_resord(n_orders, cero=(-1) * (
            n_ordenes_descartadas - 1), n_price=random.randint(1, 6))

        order_list = self.my_ordens.list_total_ordenes()

        l_res = []

        for order in order_list:
            l_res.append(self.my_mini_market.execute_request(Request(**order)))

        # print list_success_responses

        random_direction = random.choice([-1, 1])

        index_rand = random.randint(0, len(
            self.my_mini_market.orders_queue[random_direction]))

        vol_to_test = 0

        for index in range(index_rand):
            order = self.my_mini_market.orders_queue[random_direction][index]
            vol_to_test += order.size

        vol_excedent = random.randint(0, 9)

        vol_to_test += vol_excedent

        random_type = random.choice([-1, 1])



        market_order = {
            OrderKeys.size: vol_to_test,
            OrderKeys.direction: random_direction,
            OrderKeys.price: random.randint(40, 80),
            OrderKeys.id_user: self.my_ordens.counter_id.count,
            OrderKeys.group: "GROUP_" + str(random.randint(0, 1000000)),
            OrderKeys.event: 4,
            OrderKeys.type: random_type
        }

        last_trader = None

        vol_last_trader_before = None

        if index_rand < len(self.my_mini_market.orders_queue[random_direction]):
            last_trader = self.my_mini_market.orders_queue[random_direction][
                index_rand]
            vol_last_trader_before = \
                self.my_mini_market.orders_queue[random_direction][
                    index_rand].to_dict().copy()[OrderKeys.size]

        len_before = len(self.my_mini_market.orders_queue[random_direction])

        res = self.my_mini_market.execute_request(Request(**market_order))

        #print res

        len_after = len(self.my_mini_market.orders_queue[random_direction])

        if res == ExecutionResponse.OK:
            self.assertEqual(len_before, len_after + index_rand)

            if last_trader is not None:
                self.assertEqual(
                    self.my_mini_market.orders_queue[random_direction].index(
                        last_trader), 0)

                self.assertEqual(vol_last_trader_before - vol_excedent,
                             last_trader.size)


























