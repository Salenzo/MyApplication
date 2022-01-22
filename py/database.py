import json
import re
import numpy as np

def read_json(filename):
    with open(filename, encoding="utf-8") as f:
        return json.load(f)

# https://prts.wiki/w/数值范围
# 此处命名以黑板为准。
ATTRIBUTE_TYPES = [
    "max_hp", # 生命上限
    "atk", # 攻击力
    "def", # 防御力
    "magic_resistance", # 法术抗性
    "cost", # 部署费用
    "block_cnt", # 阻挡数
    "move_speed", # 移动速度
    "attack_speed", # 攻击速度（%）
    "base_attack_time", # 攻击间隔（秒）
    "reserved_0",
    "reserved_1",
    "reserved_2",
    "reserved_3",
    "hp_recovery_per_sec", # 生命回复/秒
    "sp_recovery_per_sec", # 技力回复/秒
    "ability_range_forward_extend", # 攻击范围（+格）
    "max_deploy_count", # 最大同时部署数
    "def_penetrate", # 无视防御（0~1）
    "magic_resist_penetrate", # 无视法术抗性（0~1）
    "hp_recovery_per_sec_by_max_hp_ratio",
    "taunt_level", # 嘲讽等级
    "respawn_time", # 再部署时间
    "max_deck_stack_cnt",
    "mass_level", # 重量等级
    "base_force_level",
    "def_penetrate_fixed", # 无视防御
    "one_minus_status_resistance", # 抵抗
    "magic_resist_penetrate_fixed", # 无视法术抗性
    "max_ep", # 元素上限
    "ep_recovery_per_sec",

    "stun_immune", # 眩晕抗性
    "silence_immune", # 沉默抗性
    "sleep_immune", # 沉睡抗性
    "frozen_immune", # 冻结抗性
]

CHARACTERS = read_json("excel/character_table.json")
CHARACTERS.update(read_json("excel/char_patch_table.json")["patchChars"])
UNIEQUIPS = read_json("excel/uniequip_table.json")
BATTLE_EQUIPS = read_json("excel/battle_equip_table.json")

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

# 迭代黑板列表。
# 用法：for key, value, value_str in blackboard_items(blackboard)
def blackboard_items(blackboard):
    if blackboard is None:
        return
    for item in blackboard:
        yield item["key"], item.get("value"), item.get("valueStr")

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
    # 转换属性名到蛇形，作为黑板。
    blackboard = {}
    for key, value in attributes.items():
        key = re.sub(r"(?=[A-Z])", "_", key).lower()
        blackboard[key] = value
    # 计算潜能加成。
    if potential < 0 or potential > character["maxPotentialLevel"]:
        raise ValueError("potential")
    for rank in character["potentialRanks"][:potential]:
        if rank["buff"]:
            for modifier in rank["buff"]["attributes"]["attributeModifiers"]:
                if modifier["formulaItem"] != 0:
                    raise ValueError("潜能还有不是直接加算的？")
                blackboard[ATTRIBUTE_TYPES[modifier["attributeType"]]] += modifier["value"]
    # 计算模组加成。
    if id in UNIEQUIPS["charEquip"].keys() and uniequip < len(UNIEQUIPS["charEquip"][id]):
        uniequip = BATTLE_EQUIPS[UNIEQUIPS["charEquip"][id][uniequip]]
        for key, value, _ in blackboard_items(uniequip["phases"][0]["attributeBlackboard"]):
            blackboard[key] += value
    return blackboard

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
