# -*- coding:utf-8 -*-
import cv2
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import json

import base_class as base
from base_class import LongLine


def read_json1(json_path, file):
    walls = []
    with open(json_path, 'r', encoding='utf-8') as f:
        j_data = json.load(f)

        if j_data.get('wallList') is None:
            return None
        for l in j_data.get('wallList'):
            p1 = base.Point(l['PointStart']['x'], l['PointStart']['y'])
            p2 = base.Point(l['PointEnd']['x'], l['PointEnd']['y'])
            wall = base.Line(p1, p2)
            walls.append(wall)
        thi = j_data.get('wallList')[0]['Thickness']
        dlist = walls
        plt.ion()
        figure, ax = plt.subplots()  # 后面表示分区，subplot()可以指定区域。操作命令按照就近原则
        for l in dlist:
            x = (l.points[0].x, l.points[1].x)
            y = (l.points[0].y, l.points[1].y)
            plt.plot(x, y, linewidth=thi / 100, color='r')
            # ax.add_line(Line2D(x, y, linewidth = 24, color='r'))
        plt.plot()  # 调用plot画图，有画才能显示
        plt.show()
        plt.savefig(file)
        plt.pause(1)
        plt.close()

    return walls


def draw_cle(dlist):
    # plt.ion()
    figure, ax = plt.subplots()  # 后面表示分区，subplot()可以指定区域。操作命令按照就近原则
    for l in dlist:
        x = (l.points[0].x, l.points[1].x)
        y = (l.points[0].y, l.points[1].y)
        ax.add_line(Line2D(x, y, linestyle='-', color='r'))
    plt.plot()  # 调用plot画图，有画才能显示
    plt.show()
    # plt.savefig(file)
    # plt.pause(1)
    # plt.close()


def draw_cle_test(dlist, file):
    plt.ion()
    figure, ax = plt.subplots()  # 后面表示分区，subplot()可以指定区域。操作命令按照就近原则
    for l in dlist:
        x = (l.points[0].x, l.points[1].x)
        y = (l.points[0].y, l.points[1].y)
        ax.add_line(Line2D(x, y, linestyle='-', color='r'))
    plt.plot()  # 调用plot画图，有画才能显示
    plt.show()
    plt.savefig(file)
    plt.pause(1)
    plt.close()


def draw_walls(lines, img_path, filename=None):
    img = cv2.imread(img_path, -1)

    width, height = img.shape[0], img.shape[1]

    img = img[:, :, (2, 1, 0)]  # 取列表位置元素
    figure, ax = plt.subplots()
    plt.imshow(img)
    for l in lines:
        x = (l.points[0].x, l.points[1].x)
        y = (l.points[0].y, l.points[1].y)
        ax.add_line(Line2D(x, y, linestyle='-', color='r'))
    if filename == None:
        plt.show()
    else:
        plt.savefig(filename)


def read_json(json_path):
    walls = []
    with open(json_path, 'r') as f:
        j_data = json.load(f)

        if j_data.get('result') is None:
            return None
        for l in j_data.get('result'):
            p1 = base.Point(l['p1']['x'], l['p1']['y'])
            p2 = base.Point(l['p2']['x'], l['p2']['y'])
            wall = base.Line(p1, p2)
            walls.append(wall)

    return walls


def merge_line(lines):
    hori_line = [x for x in lines if x.dim == 1]
    ver_line = [x for x in lines if x.dim == 2]
    hori_line.sort(key=lambda i: i.p1.x)
    hori_line.sort(key=lambda i: i.p1.y)

    ver_line.sort(key=lambda i: i.p1.y)
    ver_line.sort(key=lambda i: i.p1.x)

    long_line = []
    h_long_line = []
    v_long_line = []

    st = LongLine(hori_line[0])
    hori_line.__delitem__(0)
    while hori_line != []:
        if st.long_line.p2 == hori_line[0].p1:
            st.merge(hori_line[0])
            hori_line.__delitem__(0)
        else:
            h_long_line.append(st)
            st = LongLine(hori_line[0])
            hori_line.__delitem__(0)
    h_long_line.append(st)

    st = LongLine(ver_line[0])
    ver_line.__delitem__(0)
    while ver_line != []:
        if st.long_line.p2 == ver_line[0].p1:
            st.merge(ver_line[0])
            ver_line.__delitem__(0)
        else:
            v_long_line.append(st)
            st = LongLine(ver_line[0])
            ver_line.__delitem__(0)
    v_long_line.append(st)

    for l in h_long_line:
        if l.p1.y == 295:
            tag_l = l
            print('111')
        for seg in v_long_line:
            if (l.long_line.contains(seg.long_line.p1) and not (l.long_line.contains(seg.long_line.p2))) or \
                    (l.long_line.contains(seg.long_line.p2) and not (l.long_line.contains(seg.long_line.p1))):
                l.t_tag = 1
                seg.t_tag = 1
                if l.contains(seg.p1):
                    l.add_t_son(seg, seg.p1)
                else:
                    l.add_t_son(seg, seg.p2)
    for l in v_long_line:
        for seg in h_long_line:
            # if l.p1.x == 695:
            #     print('111')

            if (l.long_line.contains(seg.long_line.p1) and not (l.long_line.contains(seg.long_line.p2))) or \
                    (l.long_line.contains(seg.long_line.p2) and not (l.long_line.contains(seg.long_line.p1))):
                l.t_tag = 1
                seg.t_tag = 1
                if l.contains(seg.p1):
                    l.add_t_son(seg, seg.p1)
                else:
                    l.add_t_son(seg, seg.p2)
    long_line = h_long_line.copy()
    long_line.extend(v_long_line)

    return long_line
