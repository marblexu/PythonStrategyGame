import os
import json
import random
import pygame as pg
from . import tool
from . import constants as c
from . import map, entity

class Level(tool.State):
    def __init__(self):
        tool.State.__init__(self)
    
    def startup(self, current_time, game_info):
        # 保存状态的开始时间
        self.start_time = current_time
        # 保存游戏信息
        self.game_info = game_info
        self.loadMap()
        # 如果在地图配置文件中设置了格子信息，则读取出来
        grid = self.map_data[c.MAP_GRID] if c.MAP_GRID in self.map_data else None
        # 创建地图类
        self.map = map.Map(c.GRID_X_LEN, c.GRID_Y_LEN, grid)
        
        self.setupGroup()
        self.state = c.IDLE
    
    def loadMap(self):
        '''加载地图配置文件'''
        map_file = 'level_' + str(self.game_info[c.LEVEL_NUM]) + '.json'
        file_path = os.path.join('data', 'map', map_file)
        f = open(file_path)
        # json.load 函数将json文件内容解析后返回一个字典
        self.map_data = json.load(f)
        f.close()

    def setupGroup(self):
        self.group1 = entity.EntityGroup(0)
        self.group1.createEntity(self.map_data[c.GROUP1], self.map)

    def update(self, surface, current_time, mouse_pos):
        '''游戏的更新函数'''
        self.current_time = current_time

        if self.state == c.IDLE:
            result = self.getActiveEntity()
            if result is not None:
                entity, group = result
                self.map.active_entity = entity
                self.map.showActiveEntityRange()
                group.consumeEntity()
                self.state = c.SELECT
            else:
                self.group1.nextTurn()
        elif self.state == c.SELECT:
            if mouse_pos is not None:
                self.mouseClick(mouse_pos)
        elif self.state == c.ENTITY_ACT:
            self.group1.update(current_time, self.map)
            if self.map.active_entity.state == c.IDLE:
                self.state = c.IDLE
        if mouse_pos is not None:
            # mouse_pos 不是None，表示有鼠标点击事件
            self.mouseClick(mouse_pos)
        
        # 检查游戏状态
        self.checkGameState()
        self.draw(surface)

    def getActiveEntity(self):
        entity1 = self.group1.getActiveEntity()
        if entity1:
            entity, group = entity1, self.group1
        else:
            return None
        return (entity, group)

    def mouseClick(self, mouse_pos):
        '''有鼠标点击时，修改鼠标所在的地图格子颜色'''
        if self.map.checkMouseClick(mouse_pos):
            self.map.resetBackGround()
            self.state = c.ENTITY_ACT
    
    def checkGameState(self):
        if (self.current_time - self.start_time) > 50000:
            # 如果状态运行时间超过 5 秒，退出状态
            self.done = True
            # 使用choice 函数随机游戏结果为胜利或失败
            win = random.choice([0, 1])
            if win:
                # 如果胜利，下一个状态是关卡胜利状态
                self.next = c.LEVEL_WIN
            else:
                # 如果胜利，下一个状态是关卡失败状态
                self.next = c.LEVEL_LOSE

    def draw(self, surface):
        '''绘制游戏运行时的界面'''
        self.map.drawBackground(surface)
        self.group1.draw(surface)
        
