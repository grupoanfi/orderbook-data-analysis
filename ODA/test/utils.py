# -*- coding: utf-8 -*-

__author__ = 'grupoanfi'

import time
from collections import OrderedDict
import random as rd
import threading
from ODA.market_cols import OrderKeys


class actual_time(threading.Thread):
    def __init__(self, time):
        super(actual_time, self).__init__()
        self._sleep = 0.01
        self._time = time
        self.flag = True

    def run(self):
        while (self.flag):
            self._time.value += 0.1
            time.sleep(self._sleep)




class Counter():
    def __init__(self):
        self.count = 0

    def increase(self):
        self.count += 1


class Generear_ordenes_limit():
    def __init__(self):

        self.list_ordenes_bid = []
        self.list_ordenes_ask = []
        self.counter_id = Counter()

    def list_total_ordenes(self):

        l = []

        list_ordenana = []
        list_ordenana.extend(self.list_ordenes_ask)
        list_ordenana.extend(self.list_ordenes_bid)

        for i in range(self.total_ordenes()):
            index = rd.randint(0, len(list_ordenana) - 1)
            l.append(list_ordenana[index])
            del list_ordenana[index]

        return l


    def total_ordenes(self):
        return len(self.list_ordenes_bid) + len(self.list_ordenes_ask)


    def agregar_ordenes_bid(self, n_ordenes_bid):

        for i in range(n_ordenes_bid):
            atrib = self._generar_atrib(1, rd.randint(30, 60),
                                        rd.randint(1, 10000))
            self.list_ordenes_bid.append(atrib)

    def agregar_ordenes_ask(self, n_ordenes_ask):
        for i in range(n_ordenes_ask):
            atrib = self._generar_atrib(-1, rd.randint(30, 60),
                                        rd.randint(1, 10000))
            self.list_ordenes_ask.append(atrib)


    def _generar_atrib(self, direccion, price, vol, event=1):


        id_u = self.counter_id.count

        self.counter_id.increase()

        # vol = rd.randint(1, 10000)
        # price = rd.randint(30, 60)



        atrib = {
            OrderKeys.size: vol,
            OrderKeys.direction: direccion,
            OrderKeys.price: price,
            OrderKeys.id_user: id_u,
            OrderKeys.group: "GROUP_" + str(rd.randint(0, 1000000)),
            OrderKeys.event: event,
            OrderKeys.id_order: id_u
        }

        return atrib

    def generar_ordenes_resord(self, n_ordenes, cero=1, n_price=1):

        cont = 0
        price = 40

        while cont < n_ordenes:
            for i in range(rd.randint(1, n_price)):
                self.list_ordenes_bid.append(
                    self._generar_atrib(1, price=(price - cont),
                                        vol=(rd.randint(10, 10000))))
            for i in range(rd.randint(1, n_price)):
                self.list_ordenes_ask.append(
                    self._generar_atrib(-1, price=(price + (cero + cont)),
                                        vol=(rd.randint(10, 10000))))
            cont += 1





def tex_alearotio(id, target):
    a = chr(rd.randint(97, 122))
    b = chr(rd.randint(97, 122))
    c = chr(rd.randint(97, 122))
    d = chr(rd.randint(97, 122))

    return str(id) + '-' + str(target) + '-' + a + b + c + d












