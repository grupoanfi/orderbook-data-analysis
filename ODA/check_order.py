# -*- coding: utf-8 -*-
__author__ = 'Grupo Anfi'


# todo: Define order sintaxis

from market_cols import *


cast2int = lambda x: int(x) if x != 'None' else None
cast2float = lambda x: float(x) if x != 'None' else None

# cast_functions = dict()
# cast_functions[OrderKeys.direction] = cast2int
# cast_functions[OrderKeys.id_user] = cast2int
# cast_functions[OrderKeys.type] = cast2int
# cast_functions[OrderKeys.price] = cast2float
# cast_functions[OrderKeys.id_order] = cast2int
# cast_functions[OrderKeys.group] = cast2int
# cast_functions[OrderKeys.event] = cast2int


def cast_raw_request(req):
    """
    The method tries to parse the values of the request req, if some value
    can not be parsed then a error is raised.

    :param req: The request order to be parsed
    """
    try:
        direction = req[OrderKeys.direction]
        id_user = req[OrderKeys.id_user]
        tipo = req[OrderKeys.type]
        price = req[OrderKeys.price]
        id_order = req[OrderKeys.id_order]
        group = req[OrderKeys.group]
        event = req[OrderKeys.event]
        size = req[OrderKeys.size]
    except KeyError as e:
        print 'key missed in req:\n{0}'.format(e)
    else:
        try:
            req[OrderKeys.direction] = cast2int(direction)
            req[OrderKeys.id_user] = cast2int(id_user)
            req[OrderKeys.type] = cast2int(tipo)
            req[OrderKeys.price] = cast2float(price)
            req[OrderKeys.id_order] = cast2int(id_order)
            req[OrderKeys.group] = cast2int(group)
            req[OrderKeys.event] = cast2int(event)
            req[OrderKeys.size] = cast2float(size)
        except ValueError as v:
            print 'Ilegal data type:\n{0}'.format(v)


def check_request(req):
    """
    Check if the request is valid and returns a dict with the errors
    :param dict req: The request order
    :return tuple: Returns a tuple bool, dict
        If there is errors in the request, the the first parameter is False
        and the dict of errors contains False values
        else the first parameter is True (pass all the checks) and the dict errors
        must contain some False values

        The structure of the dict errors is {order_key: result_of_check}
    """
    ok_direction = check_direction(req)
    ok_event = check_event(req)
    ok_group = check_group(req)
    ok_id_user = check_id_user(req)
    ok_id_order = check_id_order(req)
    ok_price = check_price(req)
    ok_size = check_size(req)
    ok_type = check_type(req)

    checkpoints = dict()
    checkpoints[OrderKeys.direction] = ok_direction
    checkpoints[OrderKeys.event] = ok_event
    checkpoints[OrderKeys.group] = ok_group
    checkpoints[OrderKeys.id_user] = ok_id_user
    checkpoints[OrderKeys.id_order] = ok_id_order
    checkpoints[OrderKeys.price] = ok_price
    checkpoints[OrderKeys.size] = ok_size
    checkpoints[OrderKeys.type] = ok_type

    return all(checkpoints.values()), checkpoints


def check_direction(req):
    """
    Checks if the direction of the request is a valid direction
    :param dict req: The request order
    :return bool: True if the direction equals 1 or -1, else False
    """
    if req[OrderKeys.event] in [4]:
        return True

    try:
        return req[OrderKeys.direction] in [1, -1]
    except KeyError:
        return False


def check_event(order):
    """
    Verify if the event of the request order is in the valid event list

    :param dict order: The dict of the request order
    :return bool: True if the event value is in the valid event list, else None

    For more information about the valid events see:
    https://lobsterdata.com/info/DataStructure.php
    """
    try:
        return order[OrderKeys.event] in [1, 2, 3, 4, 5, 7]
    except KeyError:
        return False


def check_group(order):
    """
    Verify the key group is in the request order
    :param dict order: The request order
    :return bool: True in case of existence of the key, else False
    """
    return OrderKeys.group in order.keys()


def check_id_user(order):
    """
    Verify the key id_order is in the request order
    :param dict order: The request order
    :return bool: True in case of existence of the key, else False
    """
    return OrderKeys.id_user in order.keys()


def check_id_order(order):
    """
    If the order event is [2, 3] (partial deletion, total deletion respectively)
    this method verify if id_order of order is specified.

    Assumes event is validated

    :param dict order: The request order to validate
    :return bool: True if the key 'id_order' exists in order and it contains a
        id not None else False
    """
    if order[OrderKeys.event] in [2, 3]:
        return OrderKeys.id_order in order.keys() and order[OrderKeys.id_order] is not None
    else:
        #return OrderKeys.id_order not in order.keys() or order[OrderKeys.id_order] is None
        return True


def check_price(order):
    """
    This function verify if the price of a limit order (event = 1) has the correct
    datatype and his values is greater than zero.

    Assumes event, price validated

    :param dict order: The dict order
    :return:
    """
    raw_price = order[OrderKeys.price]

    if order[OrderKeys.event] in [2, 4]:
        return True

    if type(raw_price) in [float, int]:
        if order[OrderKeys.event] in [1]:
            if raw_price > 0:
                return True
            else:
                return False
        return True
    else:
        return False


def check_size(request):
    if request[OrderKeys.event] in [2]:
        return True

    try:
        return request[OrderKeys.event] in [1, 3, 4, 5] and request[OrderKeys.size] > 0
    except KeyError:
        return False


def check_type(order):
    # Assumes event is validated
    if order[OrderKeys.event] == 4:
        return OrderKeys.type in order.keys() and order[OrderKeys.type] in [-1, 1]
    else:
        return OrderKeys.type not in order.keys() or order[OrderKeys.type] is None
