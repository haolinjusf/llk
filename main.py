import os
import random
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk


class Point(object):
    """
    点类，为了更好地标识图中每个点，已经更好地进行运算（是否相等，是否是可取的点，每个点对应的植物名称等）
    """

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.img_name = ''

    def is_useful(self):
        """
        判断是否是可取的点
        """
        if self.x >= 0 and self.y >= 0:
            return True
        else:
            return False

    def __eq__(self, other) -> bool:
        """
        判断两个点是否相同
        """
        if self.x == other.x and self.y == other.y:
            return True
        return False


class MainWindow(object):
    """
    主窗口类，为了更好地定义窗口的属性和逻辑，设置入口为__init__函数(构造函数)
    """
    plants = []  # 植物名称列表
    game_title = "霄嘟连连看"  # 窗口标题
    window_width = 1300  # 窗口宽度
    window_height = 700  # 窗口长度
    icons = []  # 连连看图标列表
    icon_width = 70  # 图标宽度设置
    icon_height = 70  # 图标长度设置
    canvas_width = 1290  # canvas的宽度
    canvas_height = 690  # canvas的高度
    game_size_x = canvas_width // icon_width  # 游戏尺寸
    game_size_y = canvas_height // icon_height  # 游戏尺寸
    icon_kind = game_size_x * game_size_y // 4  # 图标种类数量（图标数量需符合要求才能开始游戏）
    map = []  # 游戏地图
    is_first = True  # 标记当前点击的方块是否是第一次点击标记值，如果是，则绘制红方块，如果不是则判断连接
    is_game_start = False  # 记录游戏是否开始
    former_point = None  # 记录前一个点
    # 以下是定义的常量
    delta_x = (canvas_width % icon_width) / 2
    delta_y = (canvas_height % icon_height) / 2
    EMPTY = -1
    NONE_LINK = 0
    STRAIGHT_LINK = 1
    ONE_CORNER_LINK = 2
    TWO_CORNER_LINK = 3

    def __init__(self):
        """
        初始化窗口
        """
        self.center_window(self.window_width, self.window_height)  # 设置窗口在屏幕的正中间
        self.menubar = tk.Menu(root)  # 设置目录栏
        self.file_menu = tk.Menu(self.menubar)  # 设置下拉栏的内容
        # self.icons = []
        self.extract_small_icon_list()
        # self.icon_kind = len(self.icons) if self.icon_kind > len(self.icons) > 0 else self.icon_kind
        self.file_menu.add_command(label="新游戏", command=self.new_game)  # 点击后，触发函数new_game
        self.menubar.add_cascade(label="游戏", menu=self.file_menu)  # 设置一个游戏目录，点击后可以看到下拉栏内容
        self.Text = tk.Label(root, text='欢迎使用植物连连看小程序\n请点击菜单栏选择游戏难度以开始游戏！( ´▽｀)',
                             justify='center', font=('微软雅黑', 20), pady=100)
        self.Text.pack()
        self.canvas = tk.Canvas()
        # 以上是设置各种组键，以下是将各种组键判定给root对象，root对象是Tk实例
        root.title(self.game_title)
        root.configure(menu=self.menubar)

    def new_game(self):
        """
        创建新游戏，初始化连连看游戏场景，并重新绘制连连看游戏场景
        """
        self.Text.forget()  # 引导文字隐藏
        self.canvas.forget()  # canvas画布隐藏，隐藏后将不会出现，如果游戏没有结束再次点击新游戏，界面会显示两个canvas的错误
        self.canvas = tk.Canvas(root, bg='white', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.TOP, pady=5)  # 新的canvas显示
        self.canvas.bind('<Button-1>', self.click_canvas)  # canvas绑定一个点击事件，点击后触发click_canvas函数
        self.is_game_start = True
        self.init_map()  # 初始化地图
        self.draw_map()  # 绘制地图

    def init_map(self):
        """
        初始化连连看游戏场景
        """
        self.map = []
        tmp_records = []
        records = []
        total = self.game_size_x * self.game_size_y
        while len(tmp_records) < total:
            for i in range(0, min(self.icon_kind, len(self.icons))):
                for j in range(0, 2):
                    tmp_records.append(i)
                if len(tmp_records) >= total:  # 检查是否已经达到总数量级了，如果达到
                    break

        for x in range(0, total):
            index = random.randint(0, len(tmp_records)-1)
            records.append(tmp_records[index])
            del tmp_records[index]

        for y in range(0, self.game_size_y):
            for x in range(0, self.game_size_x):
                if x == 0:
                    self.map.append([])
                self.map[y].append(records[x + y * self.game_size_x])

    def draw_map(self):
        """
        绘制游戏场景
        """
        self.canvas.delete("all")
        for y in range(0, self.game_size_y):
            for x in range(0, self.game_size_x):
                point = self.get_outer_left_top_point(Point(x, y))
                self.canvas.create_image((point.x, point.y), image=self.icons[self.map[y][x]], anchor='nw',
                                         tags='im%d%d' % (x, y))  # 让canvas上显示植物图片
                point.img_name = self.icons[self.map[y][x]]

    def center_window(self, width, height):
        """
        设置窗口在屏幕正中间显示
        """
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 4)
        root.geometry(size)

    def click_canvas(self, event):
        """
        设置点击事件
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
                        link_type = self.get_link_type(self.former_point, point)  # 这里获取了连通类型
                        if link_type != self.NONE_LINK:  # 如果不是无连接，则消除这两个点
                            self.clear_linked_blocks(self.former_point, point)  # 执行消除的函数
                            self.canvas.delete("rectRedOne")
                            self.is_first = True
                            # 判断游戏是否结束
                            if self.is_game_end():
                                tk.messagebox.showinfo("You Win!", "恭喜你，～你胜利啦～(⁎⁍̴̛ᴗ⁍̴̛⁎)")
                                self.is_game_start = False
                                # 结束游戏后，让canvas隐藏，引导文字显示
                                self.canvas.forget()
                                self.Text.pack()
                        else:
                            self.canvas.delete("rectRedOne")
                            self.former_point = point
                            self.draw_selected_area(point)

    def is_game_end(self):
        """
        判断游戏是否结束，如果地图中所有的点都为空，则代表游戏已经结束了
        """
        for y in range(0, self.game_size_y):
            for x in range(0, self.game_size_x):
                if self.map[y][x] != self.EMPTY:
                    return False
        return True

    def extract_small_icon_list(self):
        """
        从项目根目录中的"images"文件夹中获取图标数组
        """
        path, idx = 'images', 0
        for img in os.listdir(path):
            if img.split('.')[-1] in {'jpg', 'png'}:
                if idx >= self.icon_kind:
                    break
                ictmp = Image.open(path+'/'+img)  # 加载图像并保存到tmp_img中，保存图像名称为img
                ictmp.thumbnail((self.icon_width, self.icon_height))
                self.icons.append(ImageTk.PhotoImage(ictmp))  # 获取图片
                self.plants.append(img.split('.')[0])
                idx += 1

    def get_outer_left_top_point(self, point):
        """
        获取内部坐标对应矩形左上角顶点坐标
        """
        return Point(self.get_x(point.x), self.get_y(point.y))

    def get_outer_center_point(self, point):
        """
        获取内部坐标对应矩形中心坐标
        """
        return Point(self.get_x(point.x) + int(self.icon_width / 2),
                     self.get_y(point.y) + int(self.icon_height / 2))

    def get_x(self, x):
        return x * self.icon_width + self.delta_x

    def get_y(self, y):
        return y * self.icon_height + self.delta_y

    def get_inner_point(self, point):
        """
        获取内部坐标
        """
        x, y = -1, -1
        for i in range(0, self.game_size_x):
            x1 = self.get_x(i)
            x2 = self.get_x(i + 1)
            if x1 <= point.x < x2:
                x = i

        for j in range(0, self.game_size_y):
            j1 = self.get_y(j)
            j2 = self.get_y(j + 1)
            if j1 <= point.y < j2:
                y = j

        return Point(x, y)

    def draw_selected_area(self, point):
        """
        选择的区域变红，point为内部坐标
        """
        point_lt = self.get_outer_left_top_point(point)
        point_rb = self.get_outer_left_top_point(Point(point.x + 1, point.y + 1))
        self.canvas.create_rectangle(point_lt.x, point_lt.y, point_rb.x - 1, point_rb.y - 1,
                                     outline='red', tags="rectRedOne")  # 绘制一个红色的正方形

    def clear_linked_blocks(self, p1: Point, p2: Point):
        """
        消除连通的两个块
        """
        idx = self.map[p1.y][p1.x]
        plant_name = self.plants[idx]
        # with open(f'plant_info/{plant_name}.txt', 'r', encoding='utf-8'
        #           ) as f:  # 上次有错误是因为没有设置encoding='utf-8'，导致Windows下的编码问题
        #     plant_info = f.readlines()
        self.map[p1.y][p1.x] = self.EMPTY
        self.map[p2.y][p2.x] = self.EMPTY
        self.canvas.delete('im%d%d' % (p1.x, p1.y))
        self.canvas.delete('im%d%d' % (p2.x, p2.y))
        # messagebox.showwarning(
        #     title='植物详情',
        #     message=f'植物名称：{plant_name}\n植物介绍：{"".join(plant_info)}',
        # )  # 这是一个消息块，用于显示植物的信息，其中标题和内容如上所示

    def not_in_map(self, point):
        """
        地图上该点是否为空
        """
        if self.map[point.y][point.x] == self.EMPTY:
            return True
        else:
            return False

    def get_link_type(self, p1, p2):
        """
        获取两个点连通类型
        """
        # 首先判断两个方块中图片是否相同
        if self.map[p1.y][p1.x] != self.map[p2.y][p2.x]:
            return self.NONE_LINK
        # 是否是无需拐点的直接连接
        elif self.is_straight(p1, p2):
            return self.STRAIGHT_LINK
        # 是否是一个拐点的连接
        elif self.is_one_corner_link(p1, p2):
            return self.ONE_CORNER_LINK,
        # 是否是两个拐点的连接
        elif self.is_two_corner_link(p1, p2):
            return self.TWO_CORNER_LINK,
        # 如果都不是，则无法连接
        return self.NONE_LINK

    def is_straight(self, p1, p2):
        """
        是否为直接连接
        """
        if p1.y == p2.y:  # 是否为水平直接连接
            if p2.x < p1.x:
                start, end = p2.x, p1.x
            else:
                start, end = p1.x, p2.x
            for x in range(start + 1, end):
                if self.map[p1.y][x] != self.EMPTY:
                    return False
            return True
        elif p1.x == p2.x:  # 是否为垂直直接连接
            if p1.y > p2.y:
                start, end = p2.y, p1.y
            else:
                start, end = p1.y, p2.y
            for y in range(start + 1, end):
                if self.map[y][p1.x] != self.EMPTY:
                    return False
            return True
        return False

    def is_one_corner_link(self, p1, p2):
        """
        是否是只有一个拐点的连接。
        """
        point_corner = Point(p1.x, p2.y)
        if self.is_straight(p1, point_corner) and self.is_straight(point_corner, p2) and self.not_in_map(
                point_corner):
            return point_corner

        point_corner = Point(p2.x, p1.y)
        if self.is_straight(p1, point_corner) and self.is_straight(point_corner, p2) and self.not_in_map(
                point_corner):
            return point_corner

    def is_two_corner_link(self, p1, p2):
        """
        是否是有两个拐点的连接。
        """

        def check(id: int, p_1: Point, p_2: Point, ax: str) -> bool:
            if ax == 'x':
                id1 = p1.x
                id2 = p2.x
                gsize = self.game_size_x
            if ax == 'y':
                id1 = p1.y
                id2 = p2.y
                gsize = self.game_size_y
            if id == id1 or id == id2:
                    return False
            if id == -1 or id == gsize:
                if self.is_straight(p1, p_1) and self.is_straight(p_2, p2):
                    return True
            else:
                if self.not_in_map(p_1) and self.not_in_map(p_2):
                    if self.is_straight(p1, p_1) and self.is_straight(p_2, p_1) and self.is_straight(p_2, p2):
                        return True
            return False

        for y in range(-1, self.game_size_y+1):
            point1, point2 = Point(p1.x, y), Point(p2.x, y)
            if check(y, point1, point2, 'y'):
                return {'p1': point1, 'p2': point2}

        for x in range(-1, self.game_size_x+1):
            point1, point2 = Point(x, p1.y), Point(x, p2.y)
            if check(x, point1, point2, 'x'):
                return {'p1': point1, 'p2': point2}


root = tk.Tk()  # 创建了一个Tk实例
_ = MainWindow()  # 只是为了运行__init__函数，是以上所有程序的入口，设置了窗口的属性以及事件
root.mainloop()  # 持续显示窗口，并监听事件发生
