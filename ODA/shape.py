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
        self.__cargando_figuras()

    def __bid_normalizade(self, p_bid):
        return range(-len(p_bid), 0)

    def __ask_normalizade(self, p_ask):
        return range(1, len(p_ask) + 1)

    def __cargando_figuras(self):
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
        self.__vert_ask = [f(x) for x in xrange(self.size_k + 1)]
        self.__vert_ask = np.array(sum(self.__vert_ask, []))

        f = lambda x: [(float(x) - 0.5, 0.), (float(x) - 0.5, 0.)]
        self.__vert_bid = [f(x) for x in xrange(-(self.size_k), 1)]
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
        f = PchipInterpolator(x , y , extrapolate=True)

        domain = np.linspace(x[0], x[-1], num=self.ticks, endpoint=True)

        return [f(a) for a in domain]

    def __generator_data(self):
        """

        :return:
        """

        for orderbook in self.data:


            y_ask = [data[1] for data in orderbook[-1]]
            y_bid = [data[1] for data in orderbook[1]]

            x_ask = self.__ask_normalizade(y_ask)
            x_bid = self.__bid_normalizade(y_bid)


            yield self.__interpolate_data(x_ask, y_ask), self.__interpolate_data(x_bid, y_bid), x_ask, x_bid, y_ask, y_bid



    def __run_data(self, data):
        """

        :param data:
        :return:
        """


        ask_inter_points, bid_inter_points, x_ask, x_bid, y_ask, y_bid = data

        mid_price = (y_ask[0]  + y_bid[0])*1.0 / 2

        # print mid_price

        self.anot.set_text('Mid Price = %.1f' % mid_price)

        bid_inter_points.reverse()

        self.__update_limits_x(x_ask + x_bid)
        self.__update_limits_y(ask_inter_points + bid_inter_points)

        self.__line_bid.set_data(np.linspace(x_bid[0], x_bid[-1], num=self.ticks, endpoint=True), bid_inter_points,)
        self.__line_ask.set_data(np.linspace(x_ask[0], x_ask[-1], num=self.ticks, endpoint=True), ask_inter_points)

        bid_copy = y_bid[:]
        bid_copy.reverse()

        self.__scat.set_offsets(np.array(zip(x_bid + x_ask, bid_copy + y_ask)))

        for x, point in enumerate(y_ask):
            self.__vert_ask[x*2+1][1] = point
            self.__vert_ask[x*2+2][1] = point

        for x in xrange(len(y_ask), self.size_k):
            self.__vert_ask[x*2+1][1] = 0
            self.__vert_ask[x*2+2][1] = 0

        a = len(self.__vert_bid) - 1
        for x, point in enumerate(y_bid):
            self.__vert_bid[a-(x*2+1)][1] = point
            self.__vert_bid[a-(x*2+2)][1] = point

        for x in xrange(len(y_bid), self.size_k):
            self.__vert_bid[a-(x*2+1)][1] = 0
            self.__vert_bid[a-(x*2+2)][1] = 0

        return [self.__patch_ask, self.__patch_bid,self.__line_bid, self.__line_ask, self.__scat, self.anot]


    def __call__(self, *args, **kwargs):
        ani = animation.FuncAnimation(self.__fig, self.__run_data, self.__generator_data, blit=True, interval=30, repeat=False)
        plt.show()



def generar_orderbook_lines(n_lines):
    lines = []

    for i in xrange(n_lines):
        n_ask = random.randint(3, 6)
        ask = [(random.random() * 9 + 10, random.random() * 5 + 1) for i in xrange(n_ask)]
        ask.sort(key = lambda x: x[0])

        n_bid = random.randint(3, 6)
        bid = [(random.random() * 8 + 1, random.random() * 5 + 1) for i in xrange(n_bid)]

        lines.append({-1: ask, 1: bid})
    print lines
    return lines

if __name__ == '__main__':
    lines = generar_orderbook_lines(500)
    myshape = Shape(lines, 10)
    myshape()

    l = [(i, random.random()) for i in xrange(10)]
    k = kernelhandler(l, 0.5)
    s = [k(**{'x': x}) for x, y in l]

    print [p[1] for p in l]
    print s

    plt.plot([p[0] for p in l], [p[1] for p in l] )

    domain = np.linspace(0, 10, 100)

    plt.plot(domain, [k(**{'x': x}) for x in domain])

    plt.show()

