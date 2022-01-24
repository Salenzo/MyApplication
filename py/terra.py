import numpy as np
import database

# 这片大地。

class Tile:
    def __init__(self, row, col):
        self.row = row
        self.col = col

class PathFinder:
    def __init__(self, map, predefines):
        self.map = np.flipud(map)
        self.height, self.width = self.map.shape
        self.tiles = [
            [
                Tile(t, a)
                for a in range(self.width)
            ]
            for t in range(self.height)
        ]
        # 用法是self.passable_mask[row, col, motion_mode] → bool。
        self.passable_mask = np.moveaxis([
            # 地面单位寻找可通行地面单位且不是落穴的地块通行。
            # 有说法表示地面单位对空地块（tile_empty）也会绕行，但是游戏中没有出现在正常作战区域内的空地块，无法验证。
            # 我认为空地块可能是内部处理时地图外圈的哨兵元素。
            np.bitwise_and(np.bitwise_and(self.map, 1) != 0, np.right_shift(self.map, 8) != database.tile_keys["tile_hole"]),
            # 飞行单位寻找可通行飞行单位的地块通行。
            np.bitwise_and(self.map, 2) != 0,
        ], 0, -1)
        # 寻路算法内部使用。
        self._visited_mask = np.empty_like(self.map, dtype=np.bool8)
        self._direction_map = np.empty_like(self.map, dtype=np.int8)
        self._distance_map = np.empty_like(self.map, dtype=np.float32)
        # 放箱子时只检查有类型0检查点的路径，且只检查沿着类型0检查点能否通行（允许斜向）。
        if predefines and predefines["tokenInsts"]:
            for mm in predefines["tokenInsts"]:
                if mm["hidden"] or mm["inst"]["characterKey"] in ["箱子ID等"]:
                    self.passable_mask[mm["position"]["row"], mm["position"]["col"], 0] = False
    def getAvailableNeighbours(self, tile, allow_diagonal, motion_mode):
        t = [
            # distance, tile, direction
            (lambda t: [
                (1.414 if direction % 2 else 1) + (-1 if allow_diagonal and t and self.map[t.row, t.col] >> 8 == database.tile_keys["tile_yinyang_switch"] else 0),
                t,
                direction,
            ])(None if row < 0 or col < 0 or row >= self.height or col >= self.width else self.tiles[row][col])
            for direction, (row, col) in enumerate([
                (tile.row + 1, tile.col),
                (tile.row + 1, tile.col + 1),
                (tile.row, tile.col + 1),
                (tile.row - 1, tile.col + 1),
                (tile.row - 1, tile.col),
                (tile.row - 1, tile.col - 1),
                (tile.row, tile.col - 1),
                (tile.row + 1, tile.col - 1),
            ])
        ]
        for direction in [0, 2, 4, 6]:
            if t[direction][1] and not self.passable_mask[t[direction][1].row, t[direction][1].col, motion_mode]:
                t[direction][1] = None
                t[(direction + 1) % 8][1] = None
                t[(direction + 7) % 8][1] = None
        if not allow_diagonal:
            t = [t[0], t[2], t[4], t[6]]
        return [x for x in t if x[1] and self.passable_mask[x[1].row, x[1].col, motion_mode]]
    # motionMode：地面0还是飞行1
    def findPathBetween(self, FROM, to, motion_mode, allow_diagonal, point_data):
        if FROM["row"] < 0 or FROM["col"] < 0 or FROM["row"] >= self.height or FROM["col"] >= self.width or to["row"] < 0 or to["col"] < 0 or to["row"] >= self.height or to["col"] >= self.width:
            return None
        path = None
        # tile, distance
        queue = [(self.tiles[FROM["row"]][FROM["col"]], 0.0)]
        self._visited_mask.fill(False)
        self._direction_map.fill(-1)
        self._distance_map.fill(np.inf)
        while len(queue):
            head_tile, head_dist = queue.pop(0)
            self._visited_mask[head_tile.row, head_tile.col] = True
            if head_tile.row == to["row"] and head_tile.col == to["col"]:
                # connect pointers
                row, col = head_tile.row, head_tile.col
                path = []
                while True:
                    path.insert(0, {"row": row, "col": col})
                    direction = int(self._direction_map[row, col])
                    if direction < 0: break
                    row += (3 <= direction <= 5) - (direction <= 1 or direction >= 7)
                    col += (5 <= direction <= 7) - (1 <= direction <= 3)
                break
            for dist, tile, DIRE in self.getAvailableNeighbours(head_tile, allow_diagonal, motion_mode):
                if self._visited_mask[tile.row, tile.col]: continue
                if (self._direction_map[tile.row, tile.col] < 0
                        or (dist + head_dist < self._distance_map[tile.row, tile.col]
                            or dist + head_dist == self._distance_map[tile.row, tile.col]
                            and DIRE < self._direction_map[tile.row, tile.col])):
                    self._direction_map[tile.row, tile.col] = DIRE
                    self._distance_map[tile.row, tile.col] = dist + head_dist
                a = len(queue)
                while a > 0 and queue[a - 1][1] > head_dist: a -= 1
                queue.insert(a, (tile, head_dist + dist))
        if not path: raise Exception("Invalid path")
        path[0]["reachOffset"] = FROM.get("reachOffset")
        path[-1]["reachOffset"] = to.get("reachOffset")
        if to.get("type") in [1, 3, 5]:
            path[-1].update(point_data)
        return path
    def findPath(self, startPosition, checkpoints, endPosition, motion_mode, allow_diagonal):
        u = []
        for e in [startPosition, *[{"row": x["position"]["row"], "col": x["position"]["col"], "type": x.get("type"), "time": x.get("time"), "reachOffset": x.get("reachOffset")} for x in checkpoints], endPosition]:
            if e.get("type") in [1, 3, 5, 7]:
                u.append({**e,
                    "row": _["row"],
                    "col": _["col"],
                    "reachOffset": _["reachOffset"]
                })
            else:
                _ = e
                u.append(e)
        if any([not self.passable_mask[e["row"], e["col"], motion_mode] for e in u]):
            return u
        ret = []
        for e in range(len(u) - 1):
            if u[e].get("type") in [5, 6]: ret.append(u[e].copy())
            if u[e + 1].get("type") in [5, 6]: continue
            n = self.findPathBetween(u[e], u[e + 1], motion_mode, allow_diagonal, point_data=u[e + 1])
            t = self.merge(n, motion_mode)
            if e: t.pop(0)
            ret.extend(t)
        return ret
    def checkArea(self, a, b, motion_mode):
        return np.all(self.passable_mask[
            min(a[0], b[0]) : max(a[0], b[0]) + 1,
            min(a[1], b[1]) : max(a[1], b[1]) + 1,
            motion_mode
        ])
    def merge(self, list, motion_mode):
        if len(list) <= 2: return list
        r = None
        start = list[0]
        ret = [start]
        for point in list[1:]:
            if self.checkArea((start["row"], start["col"]), (point["row"], point["col"]), motion_mode):
                r = point
            else:
                ret.append(r)
                start = r
                if self.checkArea((start["row"], start["col"]), (point["row"], point["col"]), motion_mode):
                    r = point
        ret.append(list[-1])
        return ret

# 打印一幅二值图像。
def imprint(img):
    for row in img:
        for tile in row:
            print("[]" if tile else "--", end="")
        print()

level = database.read_json("level_act16d5_ex06.json")
pp = PathFinder(database.level_map(level), level["predefines"])
print(pp.findPath(
        { "row": 1, "col": 0 },
        [{ "position": { "row": 1, "col": 1 } }, { "position": { "row": 7, "col": 1 } }],
        { "row": 8, "col": 10 },
        0,
        True
))
