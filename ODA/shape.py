import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
from scipy.interpolate import interp1d, PchipInterpolator
import matplotlib.patches as patches
import matplotlib.path as path
from mpltools import style

__author__ = 'Math'

style.use('dark_background')


def generate_domain_line(points_ask, points_bid):
    """

    :param points_ask:
    :param points_bid:
    :return:
    """

    # mid_price = (points_ask[0][0] + points_bid[0][0]) / 2.0
    mid_size = (points_ask[0][1] + points_bid[0][1]) / 2.0

    # all_points_x = [point[0] for point in points_bid]
    # all_points_x.append(mid_price)
    # all_points_x.extend([point[0] for point in points_ask])
    # all_points_x.sort()

    all_points_y = [point[1] for point in points_bid]
    all_points_y.reverse()
    all_points_y.append(mid_size)
    all_points_y.extend([point[1] for point in points_ask])

    return all_points_y


class Shape(object):
    def __init__(self, data, size_k):
        """

        :param data:
        :param size_k:
        :return:
        """
        self.data = data
        self.__fig = None
        self.__ax = None
        self.__line = None
        self.__scat = None
        self.__patch_ask = None
        self.__patch_bid = None
        self.ticks = 500
        self.size_k = size_k
        self.__vert_ask = None
        self.__codes= None
        self.__vert_bid = None
        self.__cargando_figuras()

    def __domain_normalizade(self, p_bid, p_ask):
        """

        :param p_bid:
        :param p_ask:
        :return:
        """
        return range(-len(p_bid), len(p_ask) + 1)

    def __cargando_figuras(self):
        """

        :return:
        """
        self.__fig, self.__ax = plt.subplots()
        self.__line, = self.__ax.plot([], [], lw=5, c='blue')
        self.__scat = self.__ax.scatter([], [], c='black')

        self.__ax.set_ylim(-1, 30)
        self.__ax.set_xlim(-6, 6)
        self.__ax.grid()

        self.__vert_ask = [[(float(x) + 0.5, 0.), (float(x) + 0.5, 0.)] for x in range(self.size_k + 1)]
        self.__vert_ask = np.array(sum(self.__vert_ask, []))

        self.__vert_bid = [[(float(x) - 0.5, 0.), (float(x) - 0.5, 0.)] for x in range(-(self.size_k), 1)]
        self.__vert_bid = np.array(sum(self.__vert_bid, []))

        self.__codes = [path.Path.LINETO for i in xrange(len(self.__vert_ask))]
        self.__codes[0] = path.Path.MOVETO
        self.__codes = np.array(self.__codes)

        barpath_ask = path.Path(self.__vert_ask, self.__codes)
        self.__patch_ask = patches.PathPatch(barpath_ask, facecolor='green', edgecolor='yellow', alpha=0.4)
        self.__ax.add_patch(self.__patch_ask)

        barpath_bid = path.Path(self.__vert_bid, self.__codes)
        self.__patch_bid = patches.PathPatch(barpath_bid, facecolor='red', edgecolor='yellow', alpha=0.4)
        self.__ax.add_patch(self.__patch_bid)

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
        else:
            if abs(xmax - max_domain) > 10:
                xmax = max_domain + 3
                any_change = True

        if xmin + 2 > min_domain :
            xmin = min_domain - 2
            any_change = True
        else:
            if abs(xmin - min_domain) > 10:
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
        else:
            if abs(ymax - max_rango) > 10:
                ymax = max_rango + 3
                any_change = True

        if ymin > min_rango :
            ymin = min_rango - 2
            any_change = True
        else:
            if abs(ymin - min_rango) > 10:
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
        # f = PchipInterpolator(x,y, extrapolate=True)
        f = interp1d(x, y, kind=3)
        domain = np.linspace(x[0], x[-1], num=self.ticks, endpoint=True)
        return [f(a) for a in domain]

    def __generator_data(self):
        """

        :return:
        """

        for orderbook in self.data:

            p_ask = [data[1] for data in orderbook[-1]]
            p_bid = [data[1] for data in orderbook[1]]

            all_poinst_y = generate_domain_line(orderbook[-1], orderbook[1])
            all_poinst_x = self.__domain_normalizade(p_bid, p_ask)

            assert all_poinst_y[-len(p_ask):] == p_ask

            yield self.__interpolate_data(all_poinst_x, all_poinst_y), all_poinst_x, all_poinst_y, p_ask, p_bid

    def __run_data(self, data):
        """

        :param data:
        :return:
        """
        inter_points, domain, rango, p_ask, p_bid = data

        self.__update_limits_x(domain)
        self.__update_limits_y(inter_points)

        self.__line.set_data(np.linspace(domain[0], domain[-1], num=self.ticks, endpoint=True), inter_points)
        self.__scat.set_offsets(np.array(zip(domain, rango)))

        for x, point in enumerate(p_ask):
            self.__vert_ask[x*2+1][1] = point
            self.__vert_ask[x*2+2][1] = point

        for x in xrange(len(p_ask), self.size_k):
            self.__vert_ask[x*2+1][1] = 0
            self.__vert_ask[x*2+2][1] = 0

        a = len(self.__vert_bid) - 1
        for x, point in enumerate(p_bid):
            self.__vert_bid[a-(x*2+1)][1] = point
            self.__vert_bid[a-(x*2+2)][1] = point

        for x in xrange(len(p_bid), self.size_k):
            self.__vert_bid[a-(x*2+1)][1] = 0
            self.__vert_bid[a-(x*2+2)][1] = 0

        return [self.__patch_ask, self.__patch_bid,self.__line, self.__scat,]

    def __call__(self, *args, **kwargs):
        ani = animation.FuncAnimation(self.__fig, self.__run_data, self.__generator_data, blit=True, interval=60, repeat=False)
        plt.show()


def generar_orderbook_lines(n_lines):
    lines = []

    for i in xrange(n_lines):
        n_ask = random.randint(3, 6)
        ask = [(random.random() * 9 + 10, random.random() * 5 + 1) for i in xrange(n_ask)]

        n_bid = random.randint(3, 6)
        bid = [(random.random() * 8 + 1, random.random() * 5 + 1) for i in xrange(n_bid)]

        lines.append({-1: ask, 1: bid})
    print  lines
    return lines

if __name__ == '__main__':
    lines = generar_orderbook_lines(500)
    myshape = Shape(lines, 10)
    myshape()