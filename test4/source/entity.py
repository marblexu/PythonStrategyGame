import pygame as pg
from . import tool
from . import constants as c
from . import aStarSearch
from . import map


class Entity():
    def __init__(self, group, name, map_x, map_y):
        # 保存生物所在的生物组，生物组id ，地图位置
        self.group = group
        self.group_id = group.group_id
        self.map_x = map_x
        self.map_y = map_y
        # 加载生物的图形
        self.frames = []
        self.frame_index = 0
        self.loadFrames(name)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        # 设置生物图形显示坐标
        self.rect.centerx, self.rect.centery = self.getRectPos(map_x, map_y)

        # 生物初始状态为空闲
        self.state = c.IDLE
        # 记录生物图形切换的时间，用来实现生物行走的动画效果
        self.animate_timer = 0.0
        # 记录游戏当前时间
        self.current_time = 0.0
        # 生物行走时的速度
        self.move_speed = 2
        # 生物行走的距离
        self.distance = 4
        # 生物到目的位置的行走路径
        self.walk_path = None

    def loadFrames(self, name):
        # 加载生物的图形列表
        frame_rect_list = [(64, 0, 32, 32), (96, 0, 32, 32)]
        for frame_rect in frame_rect_list:
            self.frames.append(tool.getImage(tool.GFX[name], 
                    *frame_rect, c.BLACK, c.SIZE_MULTIPLIER))

    def getMapIndex(self):
        '''返回生物的地图位置'''
        return (self.map_x, self.map_y)

    def getRectPos(self, map_x, map_y):
        '''返回在地图格子中显示生物图形的坐标'''
        return(map_x * c.REC_SIZE + c.REC_SIZE // 2, map_y * c.REC_SIZE + c.REC_SIZE // 2)
        
    def setDestination(self, map, map_x, map_y):
        # 获取到目的位置的行走路径
        path = aStarSearch.getPath(map, (self.map_x, self.map_y), (map_x, map_y))
        if path is not None:
            # 找到一条路径，保存路径和目的坐标
            self.walk_path = path
            # 设置目的位置坐标
            self.dest_x, self.dest_y = self.getRectPos(map_x, map_y)
            # 设置下一个格子的坐标为当前位置坐标
            self.next_x, self.next_y = self.rect.centerx, self.rect.centery
            # 设置生物状态为行走状态
            self.state = c.WALK

    def getNextPosition(self):
        # 获取下一个格子的坐标
        if len(self.walk_path) > 0:
            next = self.walk_path[0]
            map_x, map_y = next.getPos()
            self.walk_path.remove(next)        
            return self.getRectPos(map_x, map_y)
        return None
 
    def walkToDestination(self):
        if self.rect.centerx == self.next_x and self.rect.centery == self.next_y:
            # 已经行走到下一个格子的坐标，继续获取再下一个格子的坐标
            pos = self.getNextPosition()
            if pos is None:
                self.state = c.IDLE
            else:
                # 保存路径中下一个格子的坐标
                self.next_x, self.next_y = pos

        # 行走到下一个格子的坐标，先移动 x 轴方向，再移动 y 轴方向
        if self.rect.centerx != self.next_x:
            if self.rect.centerx < self.next_x:
                # 向 x 轴右边移动
                self.rect.centerx += self.move_speed
                if self.rect.centerx > self.next_x:
                    # 如果大于下一个格子的 x 轴值，修正下
                    self.rect.centerx = self.next_x
            else:
                # 向 x 轴左边移动
                self.rect.centerx -= self.move_speed
                if self.rect.centerx < self.next_x:
                    # 如果小于下一个格子的 x 轴值，修正下
                    self.rect.centerx = self.next_x
        elif self.rect.centery != self.next_y:
            if self.rect.centery < self.next_y:
                # 向 y 轴下方移动
                self.rect.centery += self.move_speed
                if self.rect.centery > self.next_y:
                    # 如果大于下一个格子的 y 轴值，修正下
                    self.rect.centery = self.next_y
            else:
                # 向 y 轴上方移动
                self.rect.centery -= self.move_speed
                if self.rect.centery < self.next_y:
                    # 如果小于下一个格子的 y 轴值，修正下
                    self.rect.centery = self.next_y

    def update(self, current_time, map):
        self.current_time = current_time
        if self.state == c.WALK:
            if (self.current_time - self.animate_timer) > 200:
                # 当前图形显示时间超过 200 毫秒，切换图形索引值
                if self.frame_index == 0:
                    self.frame_index = 1
                else:
                    self.frame_index = 0
                # 更新生物图形切换的时间
                self.animate_timer = self.current_time
    
            if self.rect.centerx != self.dest_x or self.rect.centery != self.dest_y:
                # 如果还没走到目的坐标，继续行走
                self.walkToDestination()
            else:
                # 已经走到目的坐标，生物的地图位置已经改变，更新地图中生物所在的位置
                map.setEntity(self.map_x, self.map_y, None)
                self.map_x, self.map_y = map.getMapIndex(self.dest_x, self.dest_y)
                map.setEntity(self.map_x, self.map_y, self)
                # 设置行走路径为 None
                self.walk_path = None
                # 设置生物状态为空闲状态
                self.state = c.IDLE
        
        if self.state == c.IDLE:
            # 如果是空闲状态，设置图形索引值为 0
            self.frame_index = 0

    def draw(self, surface):
        # 获取当前显示的图形
        self.image = self.frames[self.frame_index]
        surface.blit(self.image, self.rect)


class EntityGroup():
    def __init__(self, group_id):
        # 生物列表
        self.group = []
        # 本生物组对象的 id 值
        self.group_id = group_id
        # 当前行动的生物在生物列表中的索引值
        self.entity_index = 0

    def createEntity(self, entity_list, map):
        for data in entity_list:
            # 获取生物的名称和地图位置
            entity_name, map_x, map_y = data['name'], data['x'], data['y']
            # 地图位置允许使用负数，类似 python 的列表负数索引值
            if map_x < 0:
                map_x = c.GRID_X_LEN + map_x
            if map_y < 0:
                map_y = c.GRID_Y_LEN + map_y
            
            # 创建生物对象，并添加到生物组
            entity = Entity(self, entity_name, map_x, map_y)
            self.group.append(entity)
            # 在地图中设置生物所在的位置
            map.setEntity(map_x, map_y, entity)

    def nextTurn(self):
        # 生物组所有生物已经行动过一轮，重新开始下一轮
        self.entity_index = 0

    def getActiveEntity(self):       
        if self.entity_index >= len(self.group):
            # 索引值大于生物数量，表示一轮行动结束，返回 None
            entity = None
        else:
            # 获取本生物组中将要行动的生物
            entity = self.group[self.entity_index]
        return entity

    def consumeEntity(self):
        # 每次生物行动结束后调用，索引值指向下一个将要行动的生物
        self.entity_index += 1

    def update(self, current_time, map):
        # 调用本生物组中所有生物的更新函数
        for entity in self.group:
            entity.update(current_time, map)

    def draw(self, surface):
        # 绘制本生物组中的所有生物图形
        for entity in self.group:
            entity.draw(surface)
