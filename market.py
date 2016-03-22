# coding: utf-8
import json

from market_cols import OrderKeys

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
