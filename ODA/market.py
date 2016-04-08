# coding: utf-8
import json
from itertools import count
from bisect import bisect_right

from market_cols import OrderKeys, ExecutionResponse, LobsterKeys, SharedValues
from orderBook import Order

__author__ = 'Grupo ANFI'

"""
This module contains the logic of order execution
All these functions assume that the sintax of the order is correct
(otherwise it will raise an exception)
check_order is in charge of such as sintax
"""


class Request(object):
    """
        This class represents the understandable objects for the Market Class,
        a request is basically a dict with the following keys:

        'direction': The direction bid:1 or sell:-1
        'event': The lobster event
        'group': The group of the trader in the case event=4
        'id_order': The id of the order in case event=1, 2, 3
        'id_user': The id_user
        'price': The price of the order
        'size': The volume of the order
        'tipo': For the trades (event=4) fill and kill or fill or kill

        depending on the event, the value of a key can or can not exist (be None).

        When a request is passed to the execute_request method, the market
        tries to process the request and always responses with a Response object
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        aux_dict = self.to_dict().copy()
        aux_dict[OrderKeys.size] = str(aux_dict[OrderKeys.size])
        return json.dumps(aux_dict)


class Response(object):
    def __init__(self, request, msg, status):
        """
        This class encapsulate all the possible responses the market can return
        when processing a request object

        :param Request request: The request order generating the response
        :param bool status: True if the request order was executed, else False
        :param str msg: A descriptive message of the happened
        :return:
        """
        self.request = request
        self.status = status
        self.msg = msg

    def was_executed(self):
        """
        Returns whether the req was or not processed successfull by the market.

            A successfull request is a transaction that produced changes in the
        orderbook.

        :return bool: True if was processed, else other cases
        """
        return self.status

    def get_event(self):
        """
        Returns the lobster event attached to this response.
        :return: An integer with the event
        """
        return self.request.event

    def __repr__(self):
        if self.status:
            return 'The following request:\n{0}\nwas SUCCESSFULLY ' \
                   'executed. DESCR: {1}'.format(self.request, self.msg)
        return 'The following request:\n{0}\nwas NOT SUCCESSFULLY executed.' \
               ' REASON: {1}'.format(self.request, self.msg)


class Market(object):
    def __init__(self, conserv_id=True):
        self.orders_queue = {LobsterKeys.bid: [], LobsterKeys.ask: []}
        self.ids_generator = count()
        self.conserv_id = conserv_id
        self.market_type = SharedValues.market_type

    @property
    def market_type(self):
        return self.__market_type

    @market_type.setter
    def market_type(self, market_type):
        if market_type not in [LobsterKeys.clean_price, LobsterKeys.dirty_price]:
            raise Exception('market_type not in [1, -1]!!!')
        self.__market_type = market_type

    def best_order(self, direction):
        """
        Returns the best order in a given direction.

        Returns None if there is none order in the given direction.

        :param direction: 1/-1: buy/sell
        :return:
        """
        try:
            return self.orders_queue[direction][0]
        except IndexError:
            return None

    def allowed_price(self, direction, price):
        """
        Check whether a limit order has an allowed price.

        :param direction:
        :param price:
        :return: True if the price is allowed, False otherwise
        """
        # todo: Make unit test
        return (self.best_order(-direction) is None) or \
               (direction * (price - self.best_price(-direction)) < 0)

    def best_price(self, direction):
        """
        Returns the best price in a given direction. Returns None if there is no
        order in the given direction.

        :param direction:
        :return:
        """
        best_order = self.best_order(direction)
        return best_order.price if best_order else None

    def find_order_byid(self, id, direction):
        """
        Finds the position of an order by id and direction. If it is not found,
        returns None.

        :param id:
        :param direction:
        :return:
        """
        try:
            pos = [order.id_order for order in
                   self.orders_queue[direction]].index(id)
            return self.orders_queue[direction][pos]
        except ValueError:
            return None

    def find_position_byid(self, id, direction):
        """
        Finds an order by id and direction. If it is not found, returns None.

        :param id:
        :param direction:
        :return:
        """
        # todo: Add unit test
        try:
            pos = [order.id_order for order in
                   self.orders_queue[direction]].index(id)
            return pos
        except ValueError:
            return None

    def execute_limit_order(self, req, conserv_id=False):
        """
        Place a limit req inside the market structure (orderbook)
        :param Request req: the Request mimit order object to process
        :return:
        """
        if self.allowed_price(req.direction, req.price):
            d = req.to_dict()
            d[OrderKeys.market_type] = self.market_type
            neworder = Order(**d)

            if not conserv_id:
                neworder.id_order = next(self.ids_generator)
            # Insert req
            newpos = bisect_right(self.orders_queue[req.direction], neworder)
            self.orders_queue[req.direction].insert(newpos, neworder)
            # Response
            return Response(req, ExecutionResponse.OK, True)
        else:
            return Response(req, ExecutionResponse.LIMITPRICEINVALID, False)

    def execute_modification(self, req):
        """
        Executes a limit order modification

        :param Request req: The requests triggering the modification.
        :return Response:
        """
        # todo: doc
        # Find req
        order_to_modify = self.find_order_byid(req.id_order, req.direction)
        if order_to_modify is None:
            return Response(req, ExecutionResponse.IDNOTFOUND, False)

        # Check modification
        if order_to_modify.group != req.group or \
                order_to_modify.id_user != req.id_user or \
                order_to_modify.price != req.price:
            return Response(req, ExecutionResponse.MODIFICATIONINVALID, False)

        # Execute modification
        order_to_modify.size = req.size
        # Response
        return Response(req, ExecutionResponse.OK, True)

    def execute_cancellation(self, req):
        """
        Process a total cancellation request, assumes the id_order is present
        in the request keys

        :param Request req: The Request object triggering the cancellation.
        :return Response:
        """
        # todo: Doc
        # todo: Unit test
        # Find req
        pos = self.find_position_byid(req.id_order, req.direction)
        if pos is None:
            return Response(req, ExecutionResponse.IDNOTFOUND, False)
        # Execute cancellation
        del self.orders_queue[req.direction][pos]

        # Response
        return Response(req, ExecutionResponse.OK, True)

    def execute_market_order(self, req):
        """
        Process a trade request

        :param request req: The Request object triggering the trade
        :return:
        """
        # todo: doc
        # todo: unit test

        # Figure out if trade is possible
        assert req.event == 4
        assert req.size > 0 and hasattr(req, OrderKeys.group)
        available_volume = sum(limit_order.size for limit_order
                               in self.orders_queue[req.direction]
                               if limit_order.group != req.group)

        # Fill or kill vs fill and kill
        assert req.type in [LobsterKeys.fill_and_kill, LobsterKeys.fill_or_kill]
        if req.type == LobsterKeys.fill_or_kill and available_volume < req.size:
            return Response(req, ExecutionResponse.ORDERNOTFILLED, False)
            # return ExecutionResponse.ORDERNOTFILLED
        elif req.type == LobsterKeys.fill_and_kill and available_volume == 0:
            return Response(req, ExecutionResponse.NOTHINGTOTRADE, False)

        # Now, we fill the trades
        limit_orders_to_delete = list()
        remaining_vol = req.size
        for pos, limit_order in enumerate(self.orders_queue[req.direction]):
            if limit_order.group != req.group:
                # Registering the new trade
                new_order = Request(**req.to_dict())
                new_order.size = min(limit_order.size, remaining_vol)
                new_order.id_order = limit_order.id_order
                # self.add_execution_message(req)
                # If the volume is exhausted, save for deletion, otherwise modify
                # immediately
                if limit_order.size == new_order.size:
                    limit_orders_to_delete.append(pos)
                else:
                    limit_order.size -= new_order.size
                # Update the remaining volume to trade
                remaining_vol -= new_order.size
                if remaining_vol == 0:
                    break

        # Delete the exhausted limit data (in reverse req for safe deletion)
        for pos in reversed(limit_orders_to_delete):
            del self.orders_queue[req.direction][pos]

        # Final response
        return Response(req, ExecutionResponse.OK, True)
        # return ExecutionResponse.OK

    def pre_trades(self, order_dict):
        # Todo: Camilo Sierra favor documentar esta función
        l_avaible_trades = [order for order in
                            self.orders_queue[order_dict[OrderKeys.direction]]
                            if order.price == order_dict[OrderKeys.price]]

        if len(l_avaible_trades) == 0:
            return False, 'ninguna orden limite con ese precio'
        else:
            l_diff_vol = []
            for order_trades in l_avaible_trades:
                if order_trades.size != order_dict[OrderKeys.size]:
                    l_diff_vol.append(order_trades)
                else:
                    break
            if len(l_diff_vol) == len(l_avaible_trades):
                return False, 'ninguna orden limite con ese volumen, vol: ' + str(
                    order_dict[OrderKeys.size]) + ', list: ' + str(
                    [order.size for order in l_diff_vol])
            else:

                for order in l_diff_vol:
                    order.group = order_dict[OrderKeys.group]

                return True, 'Ok'

    def execute_end_market(self):
        """
        Not implemented yet
        :return:
        """
        return None

    def execute_request(self, req, modify_market=True):
        """
        Executes an incoming request against the current orderbook

        :param Request req: The request order to execute
        :param modify_market: If true and the request can be executed, then
            the market is modified by the request, else only return the response
            and the market status (the orderbook) in untouched
        :return Response: The result of the request
        """
        market_status = self.orders_queue.copy()

        if req.event == LobsterKeys.add_limit_order:
            res = self.execute_limit_order(req, self.conserv_id)
        elif req.event == LobsterKeys.partial_cancellation:
            res = self.execute_modification(req)
        elif req.event == LobsterKeys.deletion:
            res = self.execute_cancellation(req)
        elif req.event == LobsterKeys.trade_visible:
            res = self.execute_market_order(req)
        elif req.event == LobsterKeys.halt_indicator:
            res = self.execute_end_market()
        else:
            raise NotImplementedError

        if not modify_market:
            self.orders_queue = market_status
        return res

    def __repr__(self):
        """
        A little representation of the market by price
        :return:
        """
        limit_orders = self.orders_queue

        bid = [o.price for o in reversed(limit_orders[self.market_type * LobsterKeys.bid])]
        ask = [o.price for o in limit_orders[self.market_type * LobsterKeys.ask]]

        return json.dumps(bid) + "|" + json.dumps(ask)

if __name__ == '__main__':
    m = Market()

