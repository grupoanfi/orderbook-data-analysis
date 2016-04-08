import json

from market_cols import OrderKeys, LobsterKeys, SharedValues
from copy import copy

__author__ = 'Math'


def orders2levels(orders_queue):
    """
    This method takes a dict of the form {1: [list of orders], -1: [list of orders]}
    and forms the orderbook by levels {1: [list of levels], -1:[list of levels]}

    assumes order by priority inside the list of orders

    :param dict orders_queue: Dictionary with the orders to parse
    :return:
    :rtype: dict of levels
    """
    levels = {LobsterKeys.bid: list(), LobsterKeys.ask: list()}

    for direction, list_orders in orders_queue.iteritems():
        if list_orders:
            curr = list_orders[0]
            levels[direction].append(Level(direction, curr.price, [curr]))
            for order in list_orders[1:]:
                if curr < order:
                    level = Level(direction, order.price, [order])
                    levels[direction].append(level)
                    curr = order
                else:
                    levels[direction][-1].add_limit_order(order)
    return levels


class Order(object):
    """
        This class represents a limit order inside the Market, the orderBook itself
         store limits orders wrapped in this class
    """

    __slots__ = [OrderKeys.direction, OrderKeys.id_user, OrderKeys.price,
                 OrderKeys.id_order, OrderKeys.group, OrderKeys.size]

    def __init__(self, **kwargs):
        for key in self.__slots__:
            setattr(self, key, kwargs[key])

    def to_dict(self):
        """
        Collects in a raw dictionary the attributes of the order.

        :return: Dictionary with the attributes
        """
        return {k: getattr(self, k) for k in self.__slots__}

    def __eq__(self, other):
        """
        Defines the equality between who orders
        :param Order other: The another order to compare
        :return bool: True if the orders are equals else False
        """
        checks = [getattr(self, k) == getattr(other, k) for k in self.__slots__]
        return all(checks)

    def __le__(self, other):
        # TODO document this overload of <
        market_type = SharedValues.market_type
        return market_type * self.direction * (self.price - other.price) >= 0

    def __lt__(self, other):
        # TODO document this overload of <=
        market_type = SharedValues.market_type
        return market_type * self.direction * (self.price - other.price) > 0

    def __repr__(self):
        market_type = SharedValues.market_type
        str_direction = LobsterKeys.mapper_direction[market_type * self.direction]
        return 'Order<side={0}, id={1}, price={2}, size={3}>'.\
            format(str_direction, self.id_order, self.price, self.size)

    def to_json(self):
        """
        JSON representation of an order.

        :return: The string representation of the order in JSON format
        """
        return json.dumps(self.to_dict())


class Level(object):
    name_orders = 'orders'
    __slots__ = [OrderKeys.direction, OrderKeys.price, name_orders]

    def __init__(self, direction, price, orders=None):
        self.direction = direction
        self.price = price

        assert type(orders) is list
        self.orders = list() if orders is None else orders

    def add_limit_order(self, order):
        """
        Adds a new limit order to the level
        :param Order order: The limit order to add
        """
        assert order.price == self.price
        self.orders.append(copy(order))

    def get_ordered_level(self):
        """
        Returns the level ordered by time
        """
        _copy = list(self.orders)
        _copy.sort(key=lambda o: o.time)
        return _copy

    def __repr__(self):
        orders = map(lambda x: x.id_order, self.orders)
        return json.dumps([self.price, orders])

    def __eq__(self, other):
        """
        This function defines the equality between two objects of the Level class

        :param Level other: Level object to compare with
        :return: True if the instances are equal else false
        """
        assert isinstance(other, Level)
        checks = list()
        checks.append(self.price == other.price)
        checks.append(len(self.orders) == len(other.orders))

        for i in xrange(len(self.orders)):
            checks.append(self.orders[i] == other.orders[i])

        return all(checks)

    def __le__(self, other):
        market_type = SharedValues.market_type
        return market_type * self.direction * (self.price - other.price) >= 0

    def __lt__(self, other):
        market_type = SharedValues.market_type
        return market_type * self.direction * (self.price - other.price) > 0


class OrderBookLine(object):
    """
    This object represents a snapshot of the orderBook file in a given time.

    A line of the orderbook is basically a list of limit orders added to the market.
    """
    __slots__ = [OrderKeys.time, 'orders_queue_levels']

    def __init__(self, time, snapshot):
        """
        Constructor of Class
        :param str time: the date in isoformat of this snapshot
        """
        self.time = time
        self.orders_queue_levels = snapshot

    def get_time(self):
        return self.time

    def to_levels(self):
        """
        There is two basic representations of the orderbook:

        1) The first representation shows the first k limit orders is both
        directions

        2) The second representation shows the first k levels in both directions
        this form, accumulates the size of the limit orders with the same price is
        an object called Level

        :return:
        """
        pass

    def add_limit_order(self, position, order):
        """
        Adds a new limit order to the row.

        :param Order order: The order instance to add
        :param position: The position in the queue to add the new order
        :return:
        """
        print position, order
        pass

    def get_info_bid(self, price):
        """
        Given a price, this method adds all the sizes of the data matching the
        price in the buy direction.
        :param float price: The level price
        :return float: The sum of all the sizes in the given level price
        """
        pass

    def get_info_ask(self, price):
        """
        Given a price, this method adds all the sizes of the data matching the
        price in the sell direction. If the level doesnot exist, return

        :param float price: The level price
        :return float: The sum of all the sizes in the given level price
        """
        pass

    def get_num_orders_buy(self):
        """
        Get the number of limit data in the buy direction
        :return int: The number of data in the buy direction
        """
        pass

    def get_num_orders_sell(self):
        """
        Get the number of limit data in the sell direction
        :return int: The number of data in the sell direction
        """
        pass

    @classmethod
    def parse_snapshot_to_levels(cls, time, snapshot):
        prices_ask = {o.price for o in snapshot[-1]}
        prices_bid = {o.price for o in snapshot[1]}

        snapshot_level = {-1: [], 1: []}

        levels_ask = [[order for order in snapshot[-1] if order.price == price]
                      for price in prices_ask]
        levels_bid = [[order for order in snapshot[1] if order.price == price]
                      for price in prices_bid]

        for _level in levels_ask:
            snapshot_level[-1].append(Level(-1, _level[0].price, _level))

        for _level in levels_bid:
            snapshot_level[1].append(Level(1, _level[0].price, _level))

        return cls(time, snapshot_level)

    def __repr__(self):
        return str(self.orders_queue_levels)


class OrderBook(object):
    def __init__(self):
        self.rows = list()
