"""这片大地（1/1）。

预测的能力是优化的前提，本模块使未经打磨的仿真运行成为可能。
"""

import numpy as np
import ptilopsis

# motion_mode：0 = 地面单位；1 = 飞行单位。
class PathFinder:
    def __init__(self, map, predefines):
        self.map = np.flipud(map)
        self.height, self.width = self.map.shape
        # 用法是self.passable_mask[row, col, motion_mode] → bool。
        self.passable_mask = np.moveaxis([
            # 地面单位寻找可通行地面单位且不是落穴的地块通行。
            # 有说法表示地面单位对空地块（tile_empty）也会绕行，但是游戏中没有出现在正常作战区域内的空地块，无法验证。
            # 我认为空地块可能是内部处理时地图外圈的哨兵元素。
            np.bitwise_and(np.bitwise_and(self.map, 1) != 0, np.right_shift(self.map, 8) != ptilopsis.tile_keys["tile_hole"]),
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
                (1.414 if direction % 2 else 1) + (-1 if allow_diagonal and t and self.map[t] >> 8 == ptilopsis.tile_keys["tile_yinyang_switch"] else 0),
                t,
                direction,
            ])(None if row < 0 or col < 0 or row >= self.height or col >= self.width else (row, col))
            for direction, (row, col) in enumerate([
                # 有时候我也希望tuple(map(sum, zip(a, b)))可以像NumPy那样写成a + b，其中a和b是元组。
                (tile[0] + 1, tile[1]),
                (tile[0] + 1, tile[1] + 1),
                (tile[0], tile[1] + 1),
                (tile[0] - 1, tile[1] + 1),
                (tile[0] - 1, tile[1]),
                (tile[0] - 1, tile[1] - 1),
                (tile[0], tile[1] - 1),
                (tile[0] + 1, tile[1] - 1),
            ])
        ]
        for direction in [0, 2, 4, 6]:
            if t[direction][1] and not self.passable_mask[t[direction][1]][motion_mode]:
                t[direction][1] = None
                t[(direction + 1) % 8][1] = None
                t[(direction + 7) % 8][1] = None
        if not allow_diagonal:
            t = [t[0], t[2], t[4], t[6]]
        return [x for x in t if x[1] and self.passable_mask[x[1]][motion_mode]]
    def path(self, FROM, to, motion_mode, allow_diagonal, point_data):
        """path搜索两点间最短路径。"""
        if FROM["row"] < 0 or FROM["col"] < 0 or FROM["row"] >= self.height or FROM["col"] >= self.width or to["row"] < 0 or to["col"] < 0 or to["row"] >= self.height or to["col"] >= self.width:
            return None
        path = None
        # tile, distance
        queue = [((FROM["row"], FROM["col"]), 0.0)]
        self._visited_mask.fill(False)
        self._direction_map.fill(-1)
        self._distance_map.fill(np.inf)
        while len(queue):
            head_tile, head_dist = queue.pop(0)
            self._visited_mask[head_tile] = True
            if head_tile[0] == to["row"] and head_tile[1] == to["col"]:
                # connect pointers
                row, col = head_tile
                path = []
                while True:
                    path.insert(0, {"row": row, "col": col})
                    direction = int(self._direction_map[row, col])
                    if direction < 0: break
                    row += (3 <= direction <= 5) - (direction <= 1 or direction >= 7)
                    col += (5 <= direction <= 7) - (1 <= direction <= 3)
                break
            for dist, tile, DIRE in self.getAvailableNeighbours(head_tile, allow_diagonal, motion_mode):
                if self._visited_mask[tile]: continue
                if (self._direction_map[tile] < 0
                        or (dist + head_dist < self._distance_map[tile]
                            or dist + head_dist == self._distance_map[tile]
                            and DIRE < self._direction_map[tile])):
                    self._direction_map[tile] = DIRE
                    self._distance_map[tile] = dist + head_dist
                a = len(queue)
                while a > 0 and queue[a - 1][1] > head_dist: a -= 1
                queue.insert(a, (tile, head_dist + dist))
        if not path: raise Exception("Invalid path")
        path[0]["reachOffset"] = FROM.get("reachOffset")
        path[-1]["reachOffset"] = to.get("reachOffset")
        if to.get("type") in [1, 3, 5]:
            path[-1].update(point_data)
        return path
    def route(self, start, checkpoints, end, motion_mode, allow_diagonal):
        """route按路线检查点分段调用path来搜索路径。"""
        u = []
        for point in [start, *[{"row": x["position"]["row"], "col": x["position"]["col"], "type": x.get("type"), "time": x.get("time"), "reachOffset": x.get("reachOffset")} for x in checkpoints], end]:
            if point.get("type") in [1, 3, 5, 7]:
                u.append({**point,
                    "row": _["row"],
                    "col": _["col"],
                    "reachOffset": _["reachOffset"]
                })
            else:
                _ = point
                u.append(point)
        if any([not self.passable_mask[e["row"], e["col"], motion_mode] for e in u]):
            return u
        ret = []
        for i in range(len(u) - 1):
            if u[i].get("type") in [5, 6]: ret.append(u[i].copy())
            if u[i + 1].get("type") in [5, 6]: continue
            ret.extend(self.clean_up_path(
                self.path(
                    u[i], u[i + 1],
                    motion_mode, allow_diagonal, point_data=u[i + 1]
                ),
                motion_mode
            )[bool(i):])
        return ret
    def clean_up_path(self, path, motion_mode):
        """合并路径中可以直走的部分。

        可以直走指的是线段端点指定的矩形内全是可通行地块。
        """
        if len(path) <= 2: return path
        ret = [path[0], path[0]]
        for point in path[1:]:
            if np.all(self.passable_mask[
                    min(ret[-2]["row"], point["row"]) : max(ret[-2]["row"], point["row"]) + 1,
                    min(ret[-2]["col"], point["col"]) : max(ret[-2]["col"], point["col"]) + 1,
                    motion_mode]):
                ret[-1] = point
            else:
                ret.append(point)
        return ret

def imprint(img):
    """打印一幅二值图像。

    真正的计算机图形学家不需要imshow，都是用print看图像的。
    """
    for row in img:
        for tile in row:
            print("[]" if tile else "--", end="")
        print()

level = ptilopsis.read_json("level_main_01-07.json")
pp = PathFinder(ptilopsis.level_map(level), level["predefines"])
print(pp.route(
        { "row": 1, "col": 0 },
        [{ "position": { "row": 1, "col": 1 } }, { "position": { "row": 7, "col": 1 } }],
        { "row": 8, "col": 10 },
        0,
        True
))
