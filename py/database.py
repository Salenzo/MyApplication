from asyncore import read
import json
import numpy as np

def read_json(filename):
    with open(filename, encoding="utf-8") as f:
        return json.load(f)

ATTRIBUTE_TYPES = [
    "maxHp", # 生命上限
    "atk", # 攻击力
    "def", # 防御力
    "magicResistance", # 法术抗性
    "cost", # 部署费用
    "blockCnt", # 阻挡数
    "moveSpeed", # 移动速度
    "attackSpeed", # 攻击速度（%）
    "baseAttackTime", # 攻击间隔（秒）
    "hpRecoveryPerSec", # 生命回复/秒
    "spRecoveryPerSec", # 技力回复/秒
    "maxDeployCount", # 最大同时部署数
    "maxDeckStackCnt",
    "tauntLevel",
    "massLevel", # 重量等级
    "baseForceLevel",
    "stunImmune", # 眩晕抗性
    "silenceImmune", # 沉默抗性
    "sleepImmune", # 沉睡抗性
    "frozenImmune", # 冻结抗性
    None,
    "respawnTime", # 再部署时间
]

CHARACTERS = read_json("excel/character_table.json")
CHARACTERS.update(read_json("excel/char_patch_table.json")["patchChars"])
UNIEQUIPS = read_json("excel/uniequip_table.json")

# 按名称和职业查找角色。
# 返回角色内部ID。
def find_character_by_name_and_profession(name, profession):
    for key, character in CHARACTERS.items():
        if character["name"] == name and character["profession"] == profession:
            return key

# 属性关键帧插值。
def interpolate_dicts(level, keyframes):
    attributes = {}
    xp = [x["level"] for x in keyframes]
    for key in keyframes[0]["data"].keys():
        fp = [x["data"][key] for x in keyframes]
        attributes[key] = np.interp(level, xp, fp)
        if type(fp[0]) is bool:
            attributes[key] = bool(attributes[key])
    return attributes

# 计算角色在指定等级处的属性。
# 内部ID，精英化阶段（0~2），等级（1~90），信赖（0~100），潜能（0~5），模组（0~）。
# 信赖是游戏显示值（0%~200%）的一半，即50以上的信赖在属性计算中视作满信赖。
# 参数名虽译得奇怪，却是来自数据库的一手命名。
def calculate_attributes(id, phase, level, favor, potential, uniequip):
    # 查询角色成长曲线。
    character = CHARACTERS[id]
    if phase < 0 or phase >= len(character["phases"]):
        raise ValueError("phase")
    phase = character["phases"][phase]
    if level < 1 or level > phase["maxLevel"]:
        raise ValueError("level")
    attributes = {"rangeId": phase["rangeId"]}
    attributes.update(interpolate_dicts(level, phase["attributesKeyFrames"]))
    # 计算信赖加成。
    if favor < 0 or favor > 100:
        raise ValueError("favor")
    for key, value in interpolate_dicts(favor, character["favorKeyFrames"]).items():
        if type(value) is not bool:
            attributes[key] += value
    # 计算潜能加成。
    if potential < 0 or potential > character["maxPotentialLevel"]:
        raise ValueError("potential")
    for rank in character["potentialRanks"][:potential]:
        if rank["buff"]:
            for modifier in rank["buff"]["attributes"]["attributeModifiers"]:
                if modifier["formulaItem"] != 0:
                    raise ValueError("天赋还有不是直接加算的？")
                attributes[ATTRIBUTE_TYPES[modifier["attributeType"]]] += modifier["value"]
    # 计算模组加成。
    if id in UNIEQUIPS["charEquip"].keys() and uniequip < len(UNIEQUIPS["charEquip"][id]):
        uniequip = UNIEQUIPS["equipDict"][UNIEQUIPS["charEquip"][id][uniequip]]
        # TODO
        print(uniequip)
    return attributes

# 转换关卡字典的地图数据到灰度图像。
# 像素值是位域：128 = 高台地形；64 = 可放置远程单位；32 = 可放置近战单位；16 = 有黑板；2 = 可通行飞行单位（猜想）；1 = 可通行地面单位。
def level_map(level):
    a = np.array(level["mapData"]["map"], dtype=np.uint8)
    if a.shape[0] != level["mapData"]["height"] or a.shape[1] != level["mapData"]["width"]:
        raise ValueError("地图数据自相矛盾：宽高与数组大小不对应")
    for row, col in np.ndindex(a.shape):
        tile = level["mapData"]["tiles"][a[row, col]]
        a[row, col] = tile["heightType"] << 7 | tile["buildableType"] << 5 | bool(tile["blackboard"]) << 4 | tile["passableMask"]
        if tile["blackboard"]:
            level["mapData"][(row, col)] = tile["blackboard"]
    return a

def main():
    print(calculate_attributes(
        find_character_by_name_and_profession("末药", "MEDIC"),
        1,14,51/2,4,0
    ))
    print(calculate_attributes(
        find_character_by_name_and_profession("格拉尼", "PIONEER"),
        2,33,33,5,1
    ))

if __name__ == "__main__":
    main()
