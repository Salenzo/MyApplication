# https://prts.wiki/w/%E5%85%AC%E5%BC%80%E6%8B%9B%E5%8B%9F#%E5%8F%8CTAG
# 仅工作于四星及以下 一星优先 五星（-1）/六星（-2）pass并提示
# data(id): [5,1,3,8,10,2] 标签id 仅工作于四星及以下 一星优先 五星（-1）/六星（-2）pass并提示
# matches: [[1,2],...] 标签id组列表 高星优先

def recruitDecide(data, matches):
    for group in matches:
        if set(group) <= set(data):
            return 9 if group == matches[0] or group == matches[1] else 3.50, group
    pass
