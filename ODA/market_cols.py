# -*- coding: utf-8 -*-
__author__ = 'Grupo Anfi'


class LobsterKeys(object):
    """
    This class defines the possible events that can be executed by the market,
    the program adopts the lobster reference for these events, for more information
    about, please visit https://lobsterdata.com/info/DataStructure.php
    """
    fill_and_kill = 1
    fill_or_kill = -1

    clean_price = 1
    dirty_price = -1

    bid = 1
    ask = -1

    add_limit_order = 1
    partial_cancellation = 2
    deletion = 3
    trade_visible = 4
    trade_hidden = 5
    halt_indicator = 7

    events = [add_limit_order, partial_cancellation, deletion, trade_visible,
              trade_hidden, halt_indicator]


class OrderKeys(object):
    """
    These strings are the keys used in the representation of a limit Order
    some of them are used too in the Requests
    """
    direction = 'direction'
    event = 'event'
    group = 'group'
    id_user = 'id_user'
    id_order = 'id_order'
    price = 'price'
    size = 'size'
    type = 'type'
    time = 'time'
    market_type = 'market_type'
    requestkeys = [direction, event, group, id_order, id_user, price, size, type,
                   time]
    executionkeys = [direction, event, group, id_order, id_user, price, size, time]


class ExecutionResponse(object):
    """
    The scope of execution errors consists in restriction given exclusively by the
    market mechanism
    """

    LIMITPRICEINVALID = 'Limit order set at price excedding the tip'
    IDNOTFOUND = 'Order id not found in cancellation or modification'
    MODIFICATIONINVALID = 'Modified order incompatible with previous order'
    ORDERNOTFILLED = 'Order not filled'
    NOTHINGTOTRADE = 'Nothing to trade'
    NOTTRADERORDER = 'this order could not be trader'
    INVALIDTRADEPRICE = 'The price of the trade is beetwen best ask price ' \
                        'and best bid price'
    OK = 'OK'

    error_list = [LIMITPRICEINVALID, IDNOTFOUND, MODIFICATIONINVALID,
                  ORDERNOTFILLED, NOTHINGTOTRADE, NOTTRADERORDER,
                  INVALIDTRADEPRICE]
