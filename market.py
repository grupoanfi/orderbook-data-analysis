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
