import queue
import numpy as np
import database

# 这片大地。
level = database.read_json("level_main_01-07.json")
level_map = database.level_map(level)

def getOrFalse(passable_mask, indices):
    return passable_mask[indices[0], indices[1]] if indices[0] >= 0 and indices[0] < passable_mask.shape[0] and indices[1] >= 0 and indices[1] < passable_mask.shape[1] else False

def getAvailableNeighbours(passable_mask, tile, allow_diagonal):
    ret = [
        {
            "dist": (1.414 if direction % 2 else 1),
            "tile": t,
            "DIRE": direction,
        }
        for direction, t in enumerate([
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
    if allow_diagonal:
        for t in ret:
            if t["tile"] is not None and t["tile"] >> 8 == database.tile_keys["tile_yinyang_switch"]:
                t["dist"] -= 1
        t = tile.map.getTileAt(t)
    for direction in [0, 2, 4, 6]:
        if not ret[direction].tile:
            ret[direction].tile = None
            ret[(direction + 1) % 8].tile = None
            ret[(direction + 7) % 8].tile = None
    if not allow_diagonal:
        ret = [ret[0], ret[2], ret[4], ret[6]]
    return [x for x in ret if getOrFalse(passable_mask, x)]

def checkArea(passable_mask, a, b):
    return np.all(passable_mask[
        min(a[0], b[0]):max(a[0], b[0]) + 1,
        min(a[1], b[1]):max(a[1], b[1]) + 1
    ])

def merge(passable_mask, list):
    if len(list) <= 2:
        return list
    a = list[0]
    b = None
    ret = [list[0]]
    for e in list[1:]:
        if checkArea(passable_mask, a, e):
            b = e
        else:
            ret.append(b)
            a = e
            if checkArea(passable_mask, a, e):
                b = e
    ret.append(list[len(list) - 1])
    return ret

modes = [
    # 地面单位寻找可通行地面单位且不是落穴的地块通行。
    # 有说法表示地面单位对空地块（tile_empty）也会绕行，但是游戏中没有出现在正常作战区域内的空地块，无法验证。
    # 我认为空地块是内部处理时地图外圈的哨兵元素，本模块中也是如此使用的。
    np.bitwise_and(np.bitwise_and(level_map, 1) != 0, np.right_shift(level_map, 8) != database.tile_keys["tile_hole"]),
    # 飞行单位寻找可通行飞行单位的地块通行。
    np.bitwise_and(level_map, 2) != 0,
]

#for row in level_map:
#    for tile in row:
#        print("[]" if tile else "--", end="")
#    print()






















class tile:
    def __init__(self, row, col, tileKey, heightType, buildableType, passableMask, map, **_):
        self.map = map
        self.row = row
        self.col = col
        self.tileKey = tileKey
        self.heightType = heightType
        self.buildableType = buildableType
        self.passableMask_raw = passableMask
        self.passableMaskOverride = None
        self.visited = False
        self.pointer = None
    def passableMask(self):
        return self.passableMaskOverride or self.passableMask_raw

class ppmap:
    def __init__(self, m):
        tiles = m["mapData"]["tiles"]
        width = m["mapData"]["width"]
        height = m["mapData"]["height"]
        routes = m["routes"]
        predefines = m["predefines"]
        self.tiles_ref = tiles.copy()
        self.width = width
        self.height = height
        self.tiles = [[tile(**self.tiles_ref[t * width + a], row=t, col=a, map=self) for a in range(width)] for t in range(height)]
        # 放箱子时只检查有类型0检查点的路径，且只检查沿着类型0检查点能否通行（允许斜向）。
        if predefines and predefines["tokenInsts"]:
            for mm in predefines["tokenInsts"]:
                if mm["hidden"] or mm["inst"]["characterKey"] in ["箱子ID等"]:
                    self.tiles[mm["position"]["row"]][mm["position"]["col"]].passableMaskOverride = 2
    def getTileAt(self, row, col):
        return None if row < 0 or col < 0 or row >= self.height or col >= self.width else self.tiles[row][col]
    def getAvailableNeighbours(self, tile, allow_diagonal, motionMode):
        t = [
            (lambda t: {
                "dist": (1.414 if direction % 2 else 1) + (-1 if allow_diagonal and t and "tile_yinyang_switch" == t.tileKey else 0),
                "tile": t,
                "DIRE": direction,
            })(self.getTileAt(t["row"], t["col"]))
            for direction, t in enumerate([
                {"row": tile.row + 1, "col": tile.col},
                {"row": tile.row + 1, "col": tile.col + 1},
                {"row": tile.row, "col": tile.col + 1},
                {"row": tile.row - 1, "col": tile.col + 1},
                {"row": tile.row - 1, "col": tile.col},
                {"row": tile.row - 1, "col": tile.col - 1},
                {"row": tile.row, "col": tile.col - 1},
                {"row": tile.row + 1, "col": tile.col - 1},
            ])
        ]
        for direction in [0, 2, 4, 6]:
            if not checkTilePassable(t[direction]["tile"], motionMode):
                t[direction]["tile"] = None
                t[(direction + 1) % 8]["tile"] = None
                t[(direction + 7) % 8]["tile"] = None
        if not allow_diagonal:
            t = [t[0], t[2], t[4], t[6]]
        return [x for x in t if checkTilePassable(x["tile"], motionMode)]
    # motionMode：地面0还是飞行1
    def findPathBetween(self, FROM, to, motionMode, allow_diagonal, point_data):
        if FROM["row"] < 0 or FROM["col"] < 0 or FROM["row"] >= self.height or FROM["col"] >= self.width or to["row"] < 0 or to["col"] < 0 or to["row"] >= self.height or to["col"] >= self.width:
            return None
        path = None
        queue = [{"dist": 0, "tile": self.getTileAt(row=FROM["row"], col=FROM["col"])}]
        while len(queue):
            head_dist = queue[0]["dist"]
            head_tile = queue.pop(0)["tile"]
            head_tile.visited = True
            if head_tile.row == to["row"] and head_tile.col == to["col"]:
                # connect pointers
                path = [{"row": head_tile.row, "col": head_tile.col}]
                p = head_tile
                while p.pointer:
                    path.insert(0, {"row": p.pointer["tile"].row, "col": p.pointer["tile"].col})
                    p = p.pointer["tile"]
                break
            for mm in [x for x in self.getAvailableNeighbours(head_tile, allow_diagonal, motionMode) if not x["tile"].visited]:
                dist = mm["dist"]
                tile = mm["tile"]
                DIRE = mm["DIRE"]
                if not tile.pointer or (dist + head_dist < tile.pointer["dist"] or dist + head_dist == tile.pointer["dist"] and DIRE < tile.pointer["direction"]):
                    tile.pointer = {"tile": head_tile, "dist": dist + head_dist, "direction": DIRE}
                if len(queue) == 0 or queue[len(queue) - 1]["dist"] < head_dist:
                    queue.append({"dist": head_dist + dist, "tile": tile})
                else:
                    a = len(queue)
                    while a > 0 and queue[a - 1]["dist"] > head_dist:
                        a -= 1
                    queue.insert(a, {"dist": head_dist + dist, "tile": tile})
        for row in range(self.height):
            for col in range(self.width):
                self.tiles[row][col].visited = False
                self.tiles[row][col].pointer = None
        if not path:
            raise Exception("Invalid path")
        path[0]["reachOffset"] = FROM.get("reachOffset")
        path[len(path) - 1]["reachOffset"] = to.get("reachOffset")
        if to.get("type") in [1, 3, 5]:
            path[path.length - 1].update(point_data)
        return path
    def findPath(self, startPosition, checkpoints, endPosition, motionMode, allowDiagonalMove):
        _ = None
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
        if any([not checkTilePassable(self.getTileAt(e["row"], e["col"]), motionMode) for e in u]):
            return u
        s = []
        for e in range(len(u) - 1):
            if u[e].get("type") in [5, 6]:
                s.append(u[e].copy())
            if u[e + 1].get("type") in [5, 6]:
                continue
            n = self.findPathBetween(u[e], u[e + 1],
                motionMode=motionMode,
                allow_diagonal=allowDiagonalMove,
                point_data=u[e + 1]
            )
            t = self.merge(n, motionMode)
            if e:
                t.pop(0)
            s.extend(t)
        return s
    def checkArea(self, FROM, to, motionMode):
        col0 = min(FROM["col"], to["col"])
        row0 = min(FROM["row"], to["row"])
        return all([all([checkTilePassable(self.tiles[row0 + row][col0 + col], motionMode) for col in range(abs(FROM["col"] - to["col"]) + 1)]) for row in range(abs(FROM["row"] - to["row"]) + 1)])
    def merge(self, list, motionMode):
        if len(list) <= 2:
            return list
        [FROM, *rest] = list
        r = None
        t = [FROM]
        for e in rest:
            if self.checkArea(FROM=FROM, to=e, motionMode=motionMode):
                r = e
            else:
                t.append(r)
                FROM = r
                if self.checkArea(FROM=FROM, to=e, motionMode=motionMode):
                    r = e
        t.append(list[len(list) - 1])
        return t

def checkTilePassable(tile, motionMode):
    return tile and tile.passableMask() & 1 << motionMode and (motionMode or tile.tileKey not in ["tile_hole", "tile_empty"])


pp = ppmap(database.read_json("level_act16d5_ex06.json"))
print(pp.findPath(
        startPosition={ "row": 1, "col": 0 },
        checkpoints=[{ "position": { "row": 1, "col": 1 } }, { "position": { "row": 7, "col": 1 } }],
        endPosition={ "row": 8, "col": 10 },
        motionMode=0,
        allowDiagonalMove=True
))
