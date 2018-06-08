# -*- coding:utf-8 -*-
import helpers
import cv2
import base_class as base
import matplotlib as plt
import os

wall_width = 10  # 数据限制有个距离就16的
wall_move_max = 100  # 孤悬在外的墙，大于这个数字认为不动


def is_adi_point(long_list, seg):
    poi_list = [seg.p1, seg.p2]
    t_type_poi_list = [[], []]
    adj_p_list = [[], []]
    h_list = [[], []]
    temp = wall_width
    # if seg.p1.y==145:
    #     print('111')
    for x in range(2):
        poi = poi_list[x]
        for i in long_list:
            if i.long_line.contains(poi) and i.long_line != seg:
                # seg已经是一条长线段，如果他的端点在i上，那他绝不会是十字形。那他只能自T字型
                if i.p1 == poi or i.p2 == poi:
                    adj_p_list[x].append(i)
                    continue
                for p in i.t_son_poi:
                    if p.get_dis(poi) <= temp and p != poi:
                        temp = p.get_dis(poi)
                        tar_line = [x[0] for x in i.t_son if x[1] == p][0]
                        t_type_poi_list[x].append([tar_line, p, i, poi, seg])
                        # 这是一个需要移动一定距离的T型点，我们暂时只考虑一个端点需要移动,双端点移动待考虑
                if t_type_poi_list[x] == []:
                    adj_p_list[x].append(i)

        if adj_p_list[x] == [] and t_type_poi_list[x] == []:
            h_list[x].append([poi, seg])
    if h_list[0] != [] or h_list[1] != []:
        # 有一个点悬挂，另一个点的可能待添加
        t = 3
        if h_list[0] != []:
            h_list = h_list[0]
            # 只传回需要的部分
        else:
            h_list = h_list[1]
    elif t_type_poi_list[0] != [] or t_type_poi_list[1] != []:
        t = 2  # T型错误，取一个进行偏移
        if t_type_poi_list[0] != []:
            t_type_poi_list = t_type_poi_list[0]
            # 只传回需要的部分
        else:
            t_type_poi_list = t_type_poi_list[1]
    else:
        t = 1

    return [t, t_type_poi_list, h_list]


def get_pra_min_dis(seg, line_list):
    tag = seg.dim
    pra_list = [x for x in line_list if x.dim == tag]
    if tag == 1:
        pra_list.sort(key=lambda x: abs(x.p1.y - seg.p1.y))
        d = abs(pra_list[1].p1.y - seg.p1.y)
    else:
        pra_list.sort(key=lambda x: abs(x.p1.x - seg.p1.x))
        d = abs(pra_list[1].p1.x - seg.p1.x)
    return [pra_list[1], d]


def is_belong(line, s):
    if line.contains(s.p1) and line.contains(s.p2):
        return True
    else:
        return False


def move_vec(l1, l2):
    # l1 原本的线，l2目标线
    if l1.dim == 1:
        # 水平
        if l1.p1.y < l2.p1.y:
            vec = base.ray_point(base.Point(0, 0), base.Point(0, 1)).vec
        else:
            vec = base.ray_point(base.Point(0, 0), base.Point(0, -1)).vec
    else:
        if l1.p1.x < l2.p1.x:
            vec = base.ray_point(base.Point(0, 0), base.Point(1, 0)).vec
        else:
            vec = base.ray_point(base.Point(0, 0), base.Point(-1, 0)).vec
    return vec


def move_line(answer, walls, lone_line_list, d_line, d_poi, t_line, mov_dis):
    for seg in lone_line_list:
        if is_belong(seg.long_line, d_line):
            lone_line = seg
            break
    vector = move_vec(d_line, t_line)

    s = lone_line.long_line

    p1 = s.p1 + vector * mov_dis
    p2 = s.p2 + vector * mov_dis
    answer.append(base.Line(p1, p2))
    walls.remove(s)

    for s in lone_line.t_son:
        # s [线和点】
        if s[1] != s[0].p1:
            start_poi = s[0].p1
            end_poi = s[0].p2
        else:
            start_poi = s[0].p2
            end_poi = s[0].p1
        end_poi = end_poi + vector * mov_dis
        answer.append(base.Line(start_poi, end_poi))
        try:
            walls.remove(s[0].long_line)
        except:
            print('可能改到同一条边了，考虑后期对有重合的线进行取交集，暂时没处理')
    return answer, walls


def run(walls):
    global remove_list
    walls_list = walls.copy()
    long_line = helpers.merge_line(walls)
    long_line = [x for x in long_line if x.t_tag == 1]
    walls = [x.long_line for x in long_line]
    # helpers.draw_cle(walls)

    answer = []
    for seg in walls:
        # for p in [seg.p1, seg.p2]:
        tag, t_type_list, hang_list = is_adi_point(long_line, seg)
        if tag == 1:
            continue

        elif tag == 2:  # t型,

            tag_line = t_type_list[-1][0]
            tag_p = t_type_list[-1][1]
            # adj_poi_line = adj_poi_list[-1][2]
            deal_poi = t_type_list[-1][3]
            deal_line = t_type_list[-1][4]
            dis = tag_p.get_dis(deal_poi)

            answer, walls = move_line(answer, walls, long_line, deal_line, deal_poi, tag_line, dis)
        elif tag == 3:
            deal_poi = hang_list[0][0]
            deal_line = hang_list[0][1]  # 空间上最近的平行线。可能会有bug，例如 远处共线
            tag_line, dis = get_pra_min_dis(deal_line, long_line)
            if dis == 0:
                if deal_poi.get_dis(tag_line.p1) <= deal_poi.get_dis(tag_line.p2):
                    tag_p = tag_line.p2
                else:
                    tag_p = tag_line.p1
                wall = base.Line(deal_poi, tag_p)
                answer.append(wall)
                # walls.append(wall)
            elif dis < wall_move_max:
                answer, walls = move_line(answer, walls, long_line, deal_line, deal_poi, tag_line, dis)  # 平移线，
    answer.extend(walls)
    return answer


def test(path):
    # path = r'C:\Users\dyrs-ai-win10\Desktop\correct_wall\result'
    save__path = r'C:\Users\dyrs-ai-win10\Desktop\correct_wall\compare'
    # name = r'\lianjia_chaoyang_daxiyangxinchengCqu_006.json'
    all_list = os.listdir(path)
    file_list = [x for x in all_list if x[-4:] == 'json']
    for fi in file_list:
        print(fi)
        f_n = path + '/' + fi

        # f_s0 = save__path + '/' + fi[:-4] + r'0.png'
        # helpers.read_json1(f_n,f_s0)


        walls = helpers.read_json(f_n)
        f_s0 = save__path + '/' + fi[:-4] + r'0.png'
        helpers.draw_cle_test(walls, f_s0)
        an = run(walls)
        f_s1 = save__path + '/' + fi[:-4] + r'1.png'
        helpers.draw_cle_test(an, f_s1)


if __name__ == "__main__":
    # test()
    path = r'C:\Users\dyrs-ai-win10\Desktop\correct_wall\result'
    # path1 = r'C:\Users\dyrs-ai-win10\Documents\Tencent Files\673722621\FileRecv\outside'
    # test(path)
    name = r'\lianjia_fs_dongguanjiayuan_010.json'
    # name1 = r'\55.json'
    walls = helpers.read_json(path + name)
    helpers.draw_cle(walls)
    an = run(walls)
    helpers.draw_cle(an)

    # helpers.read_json1(path + name1)



    # remove_list = []
    #
    # file = path + name

    # helpers.draw_cle(remove_list,color='g')
