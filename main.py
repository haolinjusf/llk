import os
import random
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

root = tk.Tk()

guide = '''
欢迎使用植物连连看小程序\n请点击菜单栏选择游戏难度以开始游戏！( ´▽｀)
'''


class Point(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.img_name = ''

    def set_img(self, img: str):
        self.img_name = img

    def is_useful(self):
        """
        判断是否是可取的点
        :return:
        """
        if self.x >= 0 and self.y >= 0:
            return True
        else:
            return False

    def __eq__(self, other) -> bool:
        """
        判断两个点是否相同
        :param other:
        :return:
        """
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def __str__(self):
        return f"x : {self.x}, y : {self.y}, img : {self.img_name}"


def center_window(width, height):
    screenwidth = root.winfo_screenwidth()
    screenheight = root.winfo_screenheight()
    size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    root.geometry(size)


class MainWindow(object):
    plants = []  # 植物名称列表
    game_title = "植物连连看"  # 窗口标题
    window_width = 600  # 窗口宽度
    window_height = 500  # 窗口长度
    icons = []  # 连连看图标列表
    game_size = 10  # 游戏尺寸
    icon_kind = game_size * game_size / 4  # 图标种类数量（图标数量需符合要求才能开始游戏）
    icon_width = 40  # 图标宽度设置
    icon_height = 40  # 图标长度设置
    canvas_width = 450
    canvas_height = 450
    map = []  # 游戏地图
    delta = 25
    is_first = True
    is_game_start = False  # 记录游戏是否开始
    former_point = None  # 记录前一个点
    EMPTY = -1
    NONE_LINK = 0
    STRAIGHT_LINK = 1
    ONE_CORNER_LINK = 2
    TWO_CORNER_LINK = 3

    def __init__(self):
        """
        初始化窗口
        """
        root.title(self.game_title)
        center_window(self.window_width, self.window_height)
        root.minsize(600, 500)

        self.__add_components()
        self.extract_small_icon_list()
        self.canvas = tk.Canvas()

    def easy_game(self):
        self.game_size = 6
        self.icon_kind = self.game_size * self.game_size / 4
        self.canvas_width = 287
        self.canvas_height = 287
        self.new_game()

    def normal_game(self):
        self.game_size = 8
        self.icon_kind = self.game_size * self.game_size / 4
        self.canvas_width = 367
        self.canvas_height = 367
        self.new_game()

    def hard_game(self):
        self.game_size = 10
        self.icon_kind = self.game_size * self.game_size / 4
        self.canvas_width = 450
        self.canvas_height = 450
        self.new_game()

    def __add_components(self):
        """
        添加组件，在窗口栏创建一个"新游戏"选项，点击选项以开始游戏。
        :return:
        """
        self.menubar = tk.Menu(root, bg="lightgrey", fg="black")
        self.file_menu = tk.Menu(self.menubar, tearoff=0, bg="lightgrey", fg="black")
        self.file_menu.add_command(label="新游戏(低难度)", command=self.easy_game)  # 点击后，触发函数new_game
        self.file_menu.add_command(label="新游戏(中难度)", command=self.normal_game)  # 点击后，触发函数new_game
        self.file_menu.add_command(label="新游戏(高难度)", command=self.hard_game)  # 点击后，触发函数new_game
        self.menubar.add_cascade(label="游戏", menu=self.file_menu)
        root.configure(menu=self.menubar)
        self.Text = tk.Label(root, text=guide, justify='center', font=('微软雅黑', 20), pady=100)
        self.Text.pack()

    def new_game(self):
        """
        创建新游戏，初始化连连看游戏场景，并重新绘制连连看游戏场景
        :return:
        """
        self.canvas.forget()
        self.Text.forget()
        self.canvas = tk.Canvas(root, bg='white', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.TOP, pady=5)
        self.canvas.bind('<Button-1>', self.click_canvas)
        self.init_map()
        self.draw_map()
        self.is_game_start = True

    def init_map(self):
        """
        初始化连连看游戏场景
        :return:
        """
        self.map = []
        tmp_records = []
        records = []
        for i in range(0, int(self.icon_kind)):
            for j in range(0, 4):
                tmp_records.append(i)

        total = self.game_size * self.game_size
        for x in range(0, total):
            index = random.randint(0, total - x - 1)
            records.append(tmp_records[index])
            del tmp_records[index]

        for y in range(0, self.game_size):
            for x in range(0, self.game_size):
                if x == 0:
                    self.map.append([])
                self.map[y].append(records[x + y * self.game_size])

    def draw_map(self):
        """
        绘制连连看游戏场景
        :return:
        """
        self.canvas.delete("all")
        for y in range(0, self.game_size):
            for x in range(0, self.game_size):
                point = self.get_outer_left_top_point(Point(x, y))
                self.canvas.create_image((point.x, point.y), image=self.icons[self.map[y][x]], anchor='nw',
                                         tags='im%d%d' % (x, y))
                point.set_img(self.icons[self.map[y][x]])

    def click_canvas(self, event):
        """
        设置点击事件
        :param event:
        :return:
        """
        if self.is_game_start:
            point = self.get_inner_point(Point(event.x, event.y))
            # 有效点击坐标
            if point.is_useful() and not self.not_in_map(point):
                if self.is_first:
                    self.draw_selected_area(point)
                    self.is_first = False
                    self.former_point = point
                else:
                    if self.former_point == point:
                        self.is_first = True
                        self.canvas.delete("rectRedOne")
                    else:
                        link_type = self.get_link_type(self.former_point, point)
                        if link_type['type'] != self.NONE_LINK:
                            self.clear_linked_blocks(self.former_point, point)
                            self.canvas.delete("rectRedOne")
                            self.is_first = True
                            if self.is_game_end():
                                tk.messagebox.showinfo("You Win!", "恭喜你，～你胜利啦～(⁎⁍̴̛ᴗ⁍̴̛⁎)")
                                self.is_game_start = False
                        else:
                            self.former_point = point
                            self.canvas.delete("rectRedOne")
                            self.draw_selected_area(point)

    def is_game_end(self):
        """
        判断游戏是否结束
        :return:
        """
        for y in range(0, self.game_size):
            for x in range(0, self.game_size):
                if self.map[y][x] != self.EMPTY:
                    return False
        return True

    def extract_small_icon_list(self):
        """
        从项目根目录中的"images"文件夹中获取图标数组
        :return:
        """
        path, idx = 'images', 0
        for img in os.listdir(path):
            if img.split('.')[-1] in {'jpg', 'png'}:
                if idx >= self.icon_kind:
                    break
                self.icons.append(ImageTk.PhotoImage(Image.open(path + '/' + img)))
                self.plants.append(img.split('.')[0])
                idx += 1

    def get_outer_left_top_point(self, point):
        """
        获取内部坐标对应矩形左上角顶点坐标
        :param point:
        :return:
        """
        return Point(self.get_x(point.x), self.get_y(point.y))

    def get_outer_center_point(self, point):
        """
        获取内部坐标对应矩形中心坐标
        :param point:
        :return:
        """
        return Point(self.get_x(point.x) + int(self.icon_width / 2),
                     self.get_y(point.y) + int(self.icon_height / 2))

    def get_x(self, x):
        return x * self.icon_width + self.delta

    def get_y(self, y):
        return y * self.icon_height + self.delta

    def get_inner_point(self, point):
        """
        获取内部坐标
        :param point:
        :return:
        """
        x = -1
        y = -1

        for i in range(0, self.game_size):
            x1 = self.get_x(i)
            x2 = self.get_x(i + 1)
            if x1 <= point.x < x2:
                x = i

        for j in range(0, self.game_size):
            j1 = self.get_y(j)
            j2 = self.get_y(j + 1)
            if j1 <= point.y < j2:
                y = j

        return Point(x, y)

    def draw_selected_area(self, point):
        """
        选择的区域变红，point为内部坐标
        :param point:
        :return:
        """
        point_lt = self.get_outer_left_top_point(point)
        point_rb = self.get_outer_left_top_point(Point(point.x + 1, point.y + 1))
        self.canvas.create_rectangle(point_lt.x, point_lt.y,
                                     point_rb.x - 1, point_rb.y - 1, outline='red', tags="rectRedOne")

    def clear_linked_blocks(self, p1: Point, p2: Point):
        """
        消除连通的两个块
        :param p1:
        :param p2:
        :return:
        """
        idx = self.map[p1.y][p1.x]
        plant_name = self.plants[idx]
        with open(f'plant_info/{plant_name}.txt', 'r') as f:
            plant_info = f.readlines()
        self.map[p1.y][p1.x] = self.EMPTY
        self.map[p2.y][p2.x] = self.EMPTY
        self.canvas.delete('im%d%d' % (p1.x, p1.y))
        self.canvas.delete('im%d%d' % (p2.x, p2.y))
        messagebox.showwarning(
            title='植物详情',
            message=f'植物名称：{plant_name}\n植物介绍：{"".join(plant_info)}',
        )

    def not_in_map(self, point):
        """
        地图上该点是否为空
        :param point:
        :return:
        """
        if self.map[point.y][point.x] == self.EMPTY:
            return True
        else:
            return False

    def get_link_type(self, p1, p2):
        """
        获取两个点连通类型
        :param p1:
        :param p2:
        :return:
        """
        # 首先判断两个方块中图片是否相同
        if self.map[p1.y][p1.x] != self.map[p2.y][p2.x]:
            return {'type': self.NONE_LINK}

        if self.is_straight(p1, p2):
            return {
                'type': self.STRAIGHT_LINK
            }
        res = self.is_one_corner_link(p1, p2)
        if res:
            return {
                'type': self.ONE_CORNER_LINK,
                'p1': res
            }
        res = self.is_two_corner_link(p1, p2)
        if res:
            return {
                'type': self.TWO_CORNER_LINK,
                'p1': res['p1'],
                'p2': res['p2']
            }
        return {
            'type': self.NONE_LINK
        }

    def is_straight(self, p1, p2):
        """
        是否为直接连接
        :param p1:
        :param p2:
        :return:
        """
        # 水平
        if p1.y == p2.y:
            # 大小判断
            if p2.x < p1.x:
                start = p2.x
                end = p1.x
            else:
                start = p1.x
                end = p2.x
            for x in range(start + 1, end):
                if self.map[p1.y][x] != self.EMPTY:
                    return False
            return True
        elif p1.x == p2.x:
            if p1.y > p2.y:
                start = p2.y
                end = p1.y
            else:
                start = p1.y
                end = p2.y
            for y in range(start + 1, end):
                if self.map[y][p1.x] != self.EMPTY:
                    return False
            return True
        return False

    def is_one_corner_link(self, p1, p2):
        point_corner = Point(p1.x, p2.y)
        if self.is_straight(p1, point_corner) and self.is_straight(point_corner, p2) and self.not_in_map(
                point_corner):
            return point_corner

        point_corner = Point(p2.x, p1.y)
        if self.is_straight(p1, point_corner) and self.is_straight(point_corner, p2) and self.not_in_map(
                point_corner):
            return point_corner

    def is_two_corner_link(self, p1, p2):

        def check(idx: int, p_1: Point, p_2: Point) -> bool:
            if idx == p1.y or idx == p2.y:
                return False
            if idx == -1 or idx == self.game_size:
                if self.is_straight(p1, p_1) and self.is_straight(p_2, p2):
                    return True
            else:
                if self.not_in_map(p_1) and self.not_in_map(p_2):
                    if self.is_straight(p1, p_1) and self.is_straight(p_2, p_1) and self.is_straight(p_2, p2):
                        return True
            return False

        for y in range(-1, self.game_size + 1):
            point1 = Point(p1.x, y)
            point2 = Point(p2.x, y)
            if check(y, point1, point2):
                return {'p1': point1, 'p2': point2}

        for x in range(-1, self.game_size + 1):
            point1 = Point(x, p1.y)
            point2 = Point(x, p2.y)
            if check(x, point1, point2):
                return {'p1': point1, 'p2': point2}


m = MainWindow()
root.mainloop()
