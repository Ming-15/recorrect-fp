# -*- coding:utf-8 -*-
import math

EPS = 1e-8


class Point(object):
    def __init__(self, x, y):
        """x: column; y: row"""
        self.x = x
        self.y = y

    def get_dis(self, p2):
        x2 = (self.x - p2.x) * (self.x - p2.x)
        y2 = (self.y - p2.y) * (self.y - p2.y)
        return math.sqrt(x2 + y2)

    def get_dim_coor(self, i):
        """
        获取dimsion相关坐标值
        i = 1, 水平的；i = 2, 垂直的
        """
        if i == 1:
            return self.x
        elif i == 2:
            return self.y
        else:
            assert "i = {0}".format(i)

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - self.y)

    def __mul__(self, other):
        return Point(other * self.x, other * self.y)


class ray_point(Point):
    def __init__(self, p1, p2):
        super(ray_point, self).__init__(p1, p2)
        self.x = p2.x - p1.x
        if self.x != 0:
            self.x = self.x / abs(self.x)
        self.y = p2.y - p1.y
        if self.y != 0:
            self.y = self.y / abs(self.y)
        self.vec = Point(self.x, self.y)


class Junction(Point):
    def __init__(self, x, y, type):
        super(Junction, self).__init__(x, y)
        self.type = type


class Element(object):
    def __init__(self, p1, p2):
        self.points = [p1, p2]
        self.name = ""
        self.id = []

    def set_id(self, id0, id1):
        self.id.append(id0)
        self.id.append(id1)


class Line(Element):
    def __init__(self, p1, p2, width=1):
        super(Line, self).__init__(p1, p2)
        self.p1 = p1
        self.p2 = p2
        self.width = width
        self.dim = self.get_dim()
        self.points_dim_coor = self.get_dim_coor(p1, p2)

        self.dir = Point(p2.x - p1.x, p2.y - p1.y)

    @property
    def length(self):
        return Point.get_dis(self.points[0], self.points[1])

    def contains(self, p):
        d1 = Point.get_dis(p, self.points[0])
        d2 = Point.get_dis(p, self.points[1])
        d = self.length
        if (d1 + d2 - d) > EPS:
            return False
        else:
            return True

    # def get_dir_coor(self, p1, p2):
    #     """
    #     获取方向相关坐标值
    #     dir = 1, 水平的；dir = 2, 垂直的
    #     """
    #     if self.dir == 1:
    #         return [p1.x, p2.x]
    #     elif self.dir == 2:
    #         return [p1.y, p2.y]
    #     # else:
    #     #     assert "i = {0}".format(self.dir)
    def get_dim_coor(self, p1, p2):
        """
        获取dimsion相关坐标值
        dir = 1, 水平的；dir = 2, 垂直的
        """
        if self.dim == 1:
            return [p1.x, p2.x]
        elif self.dim == 2:
            return [p1.y, p2.y]
            # else:
            #     assert "i = {0}".format(self.dir)

    def get_dim(self):
        dx = abs(self.points[0].x - self.points[1].x)
        dy = abs(self.points[0].y - self.points[1].y)

        dir = 0
        if dx > dy and dy <= self.width:
            dir = 1  # horizontal
        elif dx < dy and dx <= self.width:
            dir = 2  # vertical
        return dir

    def dot(self, other):
        res = self.points[0].x * other.points[1].x + self.points[0].y * other.points[1].y
        return res


class Wall(Line):
    """wall实际上是有宽度的线段"""

    def __init__(self, p1, p2, width):
        super(Wall, self).__init__(p1, p2, width)

    def contains(self, p):
        d1 = Point.get_dis(p, self.points[0])
        d2 = Point.get_dis(p, self.points[1])
        d = self.length

        if (d1 + d2 - d) > EPS:
            return False
        else:
            return True


class LongLine(Line):
    def __init__(self, l1):
        super(LongLine, self).__init__(l1.p1, l1.p2)
        self.long_line = l1
        self.son_seg = [l1]
        self.son_poi = [l1.p1, l1.p2]
        self.t_son = []
        self.t_son_poi = []
        self.t_tag = 0

    def merge(self, l2):
        if self.long_line.p2 == l2.p1:
            self.long_line = Line(self.long_line.p1, l2.p2)
            self.p1 = self.long_line.p1
            self.p2 = l2.p2
        else:
            self.long_line = Line(l2.p1, self.long_line.p2)
            self.p1 = l2.p1
            self.p2 = self.long_line.p2
        self.points = [self.p1, self.p2]
        self.son_seg.append(l2)
        if l2.p1 not in self.son_poi:
            self.son_poi.append(l2.p1)
        if l2.p2 not in self.son_poi:
            self.son_poi.append(l2.p2)
        return self.long_line

    def add_t_son(self, l, poi):
        self.t_son.append([l, poi])
        if poi not in self.son_poi:
            self.son_poi.append(poi)
            self.t_son_poi.append(poi)


class Door(Element):
    def __init__(self, p1, p2):
        super(Door, self).__init__(p1, p2)


class Label(Element):
    def __init__(self, p1, p2):
        super(Label, self).__init__(p1, p2)


class Icon(Element):
    def __init__(self, p1, p2):
        super(Icon, self).__init__(p1, p2)
