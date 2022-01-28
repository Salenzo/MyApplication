import numpy as np

# 物品id 数量 信用
data = np.zeros((10, 3), dtype=int)

# https://prts.wiki/w/%E9%87%87%E8%B4%AD%E4%B8%AD%E5%BF%83#01
# https://github.com/Kengxxiao/ArknightsGameData/blob/master/zh_CN/gamedata/excel/item_table.json
# https://penguin-stats.io/result/item
# 物品id 最低期望理智
expectedSane = {0: 3.24}


def creditDecide(data, expectedSane):
    worth = np.zeros(10, dtype=int)
    for i in range(0, 10):
        worth[i] = expectedSane[data[i][0]]*data[i][1]/data[i][2]
    return np.argsort(worth)[::-1]
