# coding: utf-8
__author__ = 'Math'

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from scipy.interpolate import interp1d, PchipInterpolator, splrep, splev
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib as mpl
from mpltools import style
from scipy.stats import gaussian_kde


mpl.rc("figure", facecolor="white")


class kernelhandler(object):
    def __init__(self, points, bandwidth):
        self.bandwidth = bandwidth
        self.points = points


    def kernel(self):
        def f(x):
            return 1.0/np.sqrt(2*np.pi)*np.exp(-1.0/2*x**2)

        return f

    def __call__(self, *args, **kwargs):
        x = kwargs['x']

        f = self.kernel()

        inter = [f((x - x_i)*1.0/self.bandwidth)*y_i for x_i, y_i in self.points]

        weigth = [f((x - x_i)*1.0/self.bandwidth) for x_i, y_i in self.points]

        return ((1.0/sum(weigth))*sum(inter))



class Shape(object):
    def __init__(self, data, size_k):
        """

        :param data:
        :param size_k:
        :return:
        """
        self.data = data
        self.size_k = size_k
        self.nodes_ask = None
        self.nondes_bid = None

        self.__fig = None
        self.__ax = None
        self.__line_bid = None
        self.__line_ask = None
        self.__scat = None
        self.__patch_ask = None
        self.__patch_bid = None
        self.anot = None
        self.ticks = 500

        self.__vert_ask = None
        self.__codes = None
        self.__vert_bid = None



    def cargando_figuras(self):
        """
        :return:
        """
        self.__fig, self.__ax = plt.subplots()
        self.__line_bid, = self.__ax.plot([], [], lw=2, c='#286090')
        self.__line_ask, = self.__ax.plot([], [], lw=2, c='#286090')
        self.__scat = self.__ax.scatter([], [], c='black', s=2)

        self.__ax.set_ylim(-1, 30)
        self.__ax.set_xlim(-6, 6)
        self.__ax.grid(linestyle='-', color='#808080', alpha=0.2)

        f = lambda x: [(float(x) + 0.5, 0.), (float(x) + 0.5, 0.)]
        self.__vert_ask = [f(x) for x in self.nodes_ask]
        self.__vert_ask = np.array(sum(self.__vert_ask, []))

        f = lambda x: [(float(x) - 0.5, 0.), (float(x) - 0.5, 0.)]
        self.__vert_bid = [f(x) for x in self.nondes_bid]
        self.__vert_bid = np.array(sum(self.__vert_bid, []))

        self.__codes = [path.Path.LINETO for _ in xrange(len(self.__vert_ask))]
        self.__codes[0] = path.Path.MOVETO
        self.__codes = np.array(self.__codes)

        barpath_ask = path.Path(self.__vert_ask, self.__codes)
        self.__patch_ask = patches.PathPatch(barpath_ask, facecolor='#5cb85c',
                                             edgecolor='#4cae4c', alpha=0.5)
        self.__ax.add_patch(self.__patch_ask)

        barpath_bid = path.Path(self.__vert_bid, self.__codes)
        self.__patch_bid = patches.PathPatch(barpath_bid, facecolor='#c9302c',
                                             edgecolor='#ac2925', alpha=0.5)
        self.__ax.add_patch(self.__patch_bid)

        # Se eliminan los ticks
        self.__ax.tick_params(width=0)

        # Se eliminan ejes
        self.__ax.spines["top"].set_visible(False)
        self.__ax.spines["right"].set_visible(False)
        self.__ax.spines["bottom"].set_visible(False)
        self.__ax.spines["left"].set_visible(False)

        self.__ax.tick_params(axis='x', colors='#404040')
        self.__ax.tick_params(axis='y', colors='#404040')

        self.anot = self.__ax.text(0.02, 0.95, '', transform=self.__ax.transAxes)


    def __update_limits_x(self, domain):
        """
        :param domain:
        :return:
        """
        xmin, xmax = self.__ax.get_xlim()

        min_domain = min(domain)
        max_domain = max(domain)

        any_change = False

        if xmax - 2 < max_domain:
            xmax = max_domain + 4
            any_change = True

        elif abs(xmax - max_domain) > 10:
                xmax = max_domain + 3
                any_change = True

        if xmin + 2 > min_domain :
            xmin = min_domain - 2
            any_change = True

        elif abs(xmin - min_domain) > 10:
                xmin = min_domain - 4
                any_change = True

        if any_change:
            self.__ax.set_xlim(xmin , xmax)
            self.__ax.figure.canvas.draw()

    def __update_limits_y(self, rango):
        """

        :param rango:
        :return:
        """

        ymin, ymax = self.__ax.get_ylim()

        min_rango = min(rango)
        max_rango = max(rango)

        any_change = False

        if ymax  < max_rango:
            ymax = max_rango + 2
            any_change = True

        elif abs(ymax - max_rango) > 10:
                ymax = max_rango + 3
                any_change = True

        if ymin > min_rango :
            ymin = min_rango - 2
            any_change = True

        elif abs(ymin - min_rango) > 10:
                ymin = min_rango - 3
                any_change = True

        if any_change:
            self.__ax.set_ylim(ymin, ymax)
            self.__ax.figure.canvas.draw()

    def __interpolate_data(self, x, y):
        """

        :param x:
        :param y:
        :return:
        """
        x1 = x[:]
        y1 = y[:]

        if sorted(x1) != x1:
            x1.reverse()
            y1.reverse()

        f = PchipInterpolator(x1 , y1 , extrapolate=True)

        domain = np.linspace(x[0], x[-1], num=self.ticks, endpoint=True)

        return [f(a) for a in domain]

    def filter_data(self, x , y):

        index = -1

        for i, data in enumerate(y):
            if data != 0 :
                index = i
                break

        if index == -1:
            return x , y

        for i in xrange(index):
            x.pop(0)
            y.pop(0)

        return x, y

    def __generator_data(self):
        """

        :return:
        """

        for orderbook in self.data:


            y_ask = [data[1] for data in orderbook[-1]]
            y_bid = [data[1] for data in orderbook[1]]

            x_ask = [data[0] for data in orderbook[-1]]
            x_bid = [data[0] for data in orderbook[1]]

            x_ask_fill, y_ask_fill=   self.filter_data(x_ask[:] , y_ask[:])
            x_bid_fill, y_bid_fill=   self.filter_data(x_bid[:] , y_bid[:])

            yield self.__interpolate_data(x_ask_fill, y_ask_fill), \
                  self.__interpolate_data(x_bid_fill, y_bid_fill), \
                  x_ask, x_bid, y_ask, y_bid, \
                  x_ask_fill, x_bid_fill, y_ask_fill, y_bid_fill




    def __run_data(self, data):
        """

        :param data:
        :return:
        """


        ask_inter_points, bid_inter_points, x_ask, x_bid, y_ask, y_bid,  x_ask_fill, x_bid_fill, y_ask_fill, y_bid_fill = data

        mid_price = (y_ask_fill[0]  + y_bid_fill[0])*1.0 / 2

        # print mid_price

        self.anot.set_text('Mid Price = %.1f' % mid_price)

        # bid_inter_points.reverse()

        x_bid.reverse()
        y_bid.reverse()

        self.__update_limits_x(x_ask + x_bid)
        self.__update_limits_y(ask_inter_points + bid_inter_points)

        self.__line_bid.set_data(np.linspace(x_bid_fill[0], x_bid_fill[-1], num=self.ticks, endpoint=True), bid_inter_points,)
        self.__line_ask.set_data(np.linspace(x_ask_fill[0], x_ask_fill[-1], num=self.ticks, endpoint=True), ask_inter_points)


        self.__scat.set_offsets(np.array(zip(x_bid_fill + x_ask_fill, y_bid_fill + y_ask_fill)))

        for x, point in enumerate(y_ask):
            self.__vert_ask[x*2+1][1] = point
            self.__vert_ask[x*2+2][1] = point

        for x in xrange(len(y_ask), self.size_k):
            self.__vert_ask[x*2+1][1] = 0
            self.__vert_ask[x*2+2][1] = 0

        y_bid.reverse()
        a = len(self.__vert_bid) - 1
        for x, point in enumerate(y_bid):
            self.__vert_bid[a-(x*2+1)][1] = point
            self.__vert_bid[a-(x*2+2)][1] = point

        for x in xrange(len(y_bid), self.size_k):
            self.__vert_bid[a-(x*2+1)][1] = 0
            self.__vert_bid[a-(x*2+2)][1] = 0

        return [self.__patch_ask, self.__patch_bid,self.__line_bid, self.__line_ask, self.__scat, self.anot]


    def __call__(self, *args, **kwargs):
        ani = animation.FuncAnimation(self.__fig, self.__run_data, self.__generator_data, blit=True, interval=100, repeat=False)
        plt.show()


class levels_to_shape(object):
    def __init__(self, data, k):
        self.data = data
        self.size_k = k
        self.aux_data = []
        self.shape = Shape(None, None)
        self.type_levels = None

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, data):

        for orderbook in data:
            # print orderbook
            domain_ask = [x[0] for x in orderbook[-1]]
            assert all(domain_ask[i] < domain_ask[i + 1] for i in xrange(len(domain_ask) - 1))

            domain_bid = [x[0] for x in orderbook[1]]
            # print domain_bid
            assert all(domain_bid[i] > domain_bid[i + 1] for i in xrange(len(domain_bid) - 1))

        self.__data = data

    def distance_to_midprice(self):

        for orderbook in self.data:

            new_orderbook = {-1: [], 1: []}

            y_ask = [data[1] for data in orderbook[-1]]
            y_bid = [data[1] for data in orderbook[1]]

            x_ask = self.__ask_normalizade(y_ask)
            x_bid = self.__bid_normalizade(y_bid)

            new_orderbook[-1] = zip(x_ask, y_ask)
            new_orderbook[1] = zip(x_bid, y_bid)

            self.aux_data.append(new_orderbook)

            # print new_orderbook[-1]
            # print new_orderbook[1]
            # exit()

        self.type_levels = 'mid_price'
        self.set_nodes_barr()

    def distance_to_extreme(self):

        for orderbook in self.data:

            new_orderbook = {-1: [], 1: []}

            y_ask = [data[1] for data in orderbook[-1]]
            y_bid = [data[1] for data in orderbook[1]]

            len_ask = len(y_ask)
            len_bid = len(y_bid)

            x_ask = [len_bid + i for i in xrange(len_ask)]
            x_bid = [-(len_ask+i)  for i in xrange(len_bid)]

            new_orderbook[-1] = zip(x_ask, y_ask)
            new_orderbook[1] = zip(x_bid, y_bid)
            #
            # print len_bid
            # print len_ask
            # print new_orderbook[-1]
            # print new_orderbook[1]
            # exit()

            for i in xrange(0, abs(x_bid[0]) - 1):
                new_orderbook[1].insert(i, (-(i+1), 0))

            for i in xrange(1, x_ask[0]):
                new_orderbook[-1].insert(i - 1, (i, 0))

            # print new_orderbook[-1]
            # print new_orderbook[1]
            # exit()


            self.aux_data.append(new_orderbook)

        self.type_levels = 'extreme'
        self.set_nodes_barr()

    def set_nodes_barr(self):

        if self.type_levels == 'mid_price':

            nodes_ask = xrange(self.size_k + 1)
            nodes_bid = xrange(-(self.size_k), 1)

            self.shape.nondes_bid = nodes_bid
            self.shape.nodes_ask = nodes_ask
            self.shape.size_k = self.size_k

        elif self.type_levels == 'extreme':

            nodes_ask = xrange(self.size_k*2 + 1)
            nodes_bid = xrange(-(self.size_k*2), 1)

            self.shape.nondes_bid = nodes_bid
            self.shape.nodes_ask = nodes_ask
            self.shape.size_k = self.size_k*2


    def draw_shape(self):
        self.shape.data = self.aux_data
        self.shape.cargando_figuras()
        self.shape()


    def __bid_normalizade(self, p_bid):
        l = range(-len(p_bid), 0)
        l.reverse()
        return l

    def __ask_normalizade(self, p_ask):
        return range(1, len(p_ask) + 1)


def generar_orderbook_lines(n_lines):
    lines = []

    for i in xrange(n_lines):
        n_ask = random.randint(1, 4)
        ask = [(i, random.random() * 5 + 1) for i in xrange(0, 10, n_ask)]
        ask.sort(key = lambda x: x[0])

        n_bid = random.randint(1, 4)
        bid = [(-(i+1), random.random() * 5 + 1) for i in xrange(0, 10, n_bid)]

        lines.append({-1: ask, 1: bid})
    print lines
    return lines

if __name__ == '__main__':
    lines = generar_orderbook_lines(500)

    levels = levels_to_shape(lines, 10)
    levels.distance_to_midprice()
    # levels.distance_to_extreme()
    levels.draw_shape()

    # l = [(i, random.random()) for i in xrange(10)]
    # k = kernelhandler(l, 0.5)
    # s = [k(**{'x': x}) for x, y in l]
    #
    # print [p[1] for p in l]
    # print s
    #
    # plt.plot([p[0] for p in l], [p[1] for p in l] )
    #
    # domain = np.linspace(0, 10, 100)
    #
    # plt.plot(domain, [k(**{'x': x}) for x in domain])
    #
    # plt.show()

