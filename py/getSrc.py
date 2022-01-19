import os
import requests

root = './src/'


def getPics(root, dict):
    createFolder(root)
    for key in dict:
        createFolder(key)
        for i in range(1, 3):
            if i == 1:
                save(root+key+'/'+'avatar_'+'raw'+'_'+i+'.png', requests.get(
                    'https://prts.wiki/images/d/de/%E5%A4%B4%E5%83%8F_'+dict[key]+'.png').content)
                save(root+key+'/'+'halfBody_'+'raw'+'_'+i+'.png', requests.get(
                    'https://prts.wiki/images/d/de/%E5%8D%8A%E8%BA%AB%E5%83%8F_'+dict[key]+'.png').content)
                continue
            try:
                save(root+key+'/'+'avatar_'+'raw'+'_'+i+'.png', requests.get(
                    'https://prts.wiki/images/d/de/%E5%A4%B4%E5%83%8F_'+dict[key]+'_'+i+'.png').content)
                save(root+key+'/'+'halfBody_'+'raw'+'_'+i+'.png', requests.get(
                    'https://prts.wiki/images/d/de/%E5%8D%8A%E8%BA%AB%E5%83%8F_'+dict[key]+'_'+i+'.png').content)
            except Exception as e:
                break
        for i in range(1, 9):
            try:
                save(root+key+'/'+'avatar_'+'skin'+'_'+i+'.png', requests.get(
                    'https://prts.wiki/images/d/de/%E5%A4%B4%E5%83%8F_'+dict[key]+'_skin'+i+'.png').content)
                save(root+key+'/'+'halfBody_'+'skin'+'_'+i+'.png', requests.get(
                    'https://prts.wiki/images/d/de/%E5%8D%8A%E8%BA%AB%E5%83%8F_'+dict[key]+'_skin'+i+'.png').content)
            except Exception as e:
                break


def createFolder(path):
    if os.path.exists(path) == False:
        os.makedirs(path)


def save(path, pic):
    with open(path, 'wb') as file:
        file.write(pic)
        file.flush()
