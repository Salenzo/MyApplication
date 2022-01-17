 # character_table.json

```javascript
enum FormulaItemType {
	ADDITION,
	MULTIPLIER,
	FINAL_ADDITION,
	FINAL_SCALER,
}
_Blackboard = {
	"key": string,
	"value": number,
	"valueStr": null, // 没有出现在character_table和skill_table中
};
_KeyFrame = {
	"level": number,
	"data": {
		"maxHp": number,
		"atk": number,
		"def": number,
		"magicResistance": number,
		"cost": number,
		"blockCnt": number,
		"moveSpeed": number,
		"attackSpeed": number,
		"baseAttackTime": number,
		"respawnTime": number,
		"hpRecoveryPerSec": number,
		"spRecoveryPerSec": number,
		"maxDeployCount": number,
		"maxDeckStackCnt": number,
		"tauntLevel": number,
		"massLevel": number,
		"baseForceLevel": number,
		"stunImmune": bool,
		"silenceImmune": bool,
		"sleepImmune": bool,
		"frozenImmune": bool,
	},
};
_UnlockCond = {
	"phase": number,
	"level": number,
};
_Cost = {
	"id": string,
	"count": number,
	"type": "MATERIAL",
};
{
	"name": string,
	"description": string?,
	"canUseGeneralPotentialItem": bool,
	"potentialItemId": string,
	"nationId": string?,
	"groupId": string?,
	"teamId": string?,
	"displayNumber": string?,
	"tokenKey": string?,
	"appellation": string,
	"position": ["ALL", "MELEE", "NONE", "RANGED"],
	"tagList": arrayOf(["位移", "减速", "削弱", "召唤", "快速复活", "控场", "支援", "新手", "治疗", "爆发", "生存", "群攻", "费用回复", "输出", "防护"])?,
	"itemUsage": string?,
	"itemDesc": string?,
	"itemObtainApproach": ["主线剧情", "信用交易所", "凭证交易所", "周年奖励", "招募寻访", "招募寻访见习任务", "活动获得", "限时礼包", "集成战略获得"]?,
	"isNotObtainable": bool,
	"isSpChar": bool,
	"maxPotentialLevel": number,
	"rarity": number,
	"profession": ["CASTER", "MEDIC", "PIONEER", "SNIPER", "SPECIAL", "SUPPORT", "TANK", "TOKEN", "TRAP", "WARRIOR"],
	"subProfessionId": ["aoesniper", "artsfghter", "artsprotector", "bard", "bearer", "blastcaster", "blessing", "bombarder", "centurion", "chain", "charger", "closerange", "corecaster", "craftsman", "dollkeeper", "duelist", "executor", "fastshot", "fearless", "fighter", "fortress", "funnel", "geek", "guardian", "healer", "hookmaster", "instructor", "librator", "longrange", "lord", "merchant", "musha", "mystic", "notchar1", "notchar2", "phalanx", "physician", "pioneer", "protector", "pusher", "reaper", "reaperrange", "ringhealer", "siegesniper", "slower", "splashcaster", "stalker", "summoner", "sword", "tactician", "traper", "underminer", "unyield", "wandermedic"],
	"trait": {
		"candidates": arrayOf({
			"unlockCondition": _UnlockCond,
			"requiredPotentialRank": number,
			"blackboard": arrayOf(_Blackboard),
			"overrideDescripton": string?,
			"prefabKey": string?,
			"rangeId": string?,
		}),
	}?,
	"phases": arrayOf({
		"characterPrefabKey": string,
		"rangeId": string?,
		"maxLevel": number,
		"attributesKeyFrames": arrayOf(_KeyFrame),
		"evolveCost": arrayOf(_Cost)?,
	}),
	"skills": arrayOf({
		"skillId": string?,
		"overridePrefabKey": string?,
		"overrideTokenKey": string?,
		"levelUpCostCond": arrayOf({
			"unlockCond": _UnlockCond,
			"lvlUpTime": number,
			"levelUpCost": arrayOf(_Cost)?,
		}),
		"unlockCond": _UnlockCond,
	}),
	"talents": arrayOf({
		"candidates": arrayOf({
			"unlockCondition": _UnlockCond,
			"requiredPotentialRank": number,
			"prefabKey": string,
			"name": string?,
			"description": string?,
			"rangeId": ["b1", "the11", "the31", "x4", "x5"]?,
			"blackboard": arrayOf(_Blackboard),
		})?,
	})?,
	"potentialRanks": arrayOf({
		"type": (0=属性提升；1=天赋加强),
		"description": string,
		"buff": {
			"attributes": {
				"abnormalFlags": null,
				"abnormalImmunes": null,
				"abnormalAntis": null,
				"abnormalCombos": null,
				"abnormalComboImmunes": null,
				"attributeModifiers": arrayOf({
					"attributeType": number,
					"formulaItem": enum FormulaItemType, // 天赋增益算法皆为0（直接加算）
					"value": number,
					"loadFromBlackboard": false,
					"fetchBaseValueFromSourceEntity": false,
				}),
			},
		}?,
		"equivalentCost": null,
	}),
	"favorKeyFrames": arrayOf(_KeyFrame)?,
	"allSkillLvlup": arrayOf({
		"unlockCond": _UnlockCond,
		"lvlUpCost": arrayOf(_Cost)?,
	}),
}
```

# skill_table.json

```javascript
{
	"skillId": string,
	"iconId": string?,
	"hidden": bool,
	"levels": arrayOf({
		"name": string,
		"rangeId": ["the01", "the11", "the12", "the13", "the21", "the22", "the23", "the25", "the26", "the31", "the310", "the312", "the313", "the314", "the315", "the316", "the32", "the33", "the34", "the37", "the41", "x1", "x2", "x3", "x4", "x5", "x6", "y4", "y7", "y8"]?,
		"description": string,
		"skillType": number,
		"spData": {
			"spType": number,
			"levelUpCost": any,
			"maxChargeTime": number,
			"spCost": number,
			"initSp": number,
			"increment": number,
		},
		"prefabId": string?,
		"duration": number,
		"blackboard": arrayOf(_Blackboard),
	}),
}
```

# level_a001_06.json

```javascript
const _Id = oneOfType(['enemy1000_Gopro', 'enemy1000_Gopro3', 'enemy1001_Bigbo', 'enemy1003_Ncbow2', 'enemy1008_Ghost']);
_SpawnOffset = {
	"x": number,
	"y": number,
};
_Position = {
	"row": number,
	"col": number,
};
{
	"options": {
		"characterLimit": number,
		"maxLifePoint": number,
		"initialCost": number,
		"maxCost": number,
		"costIncreaseTime": number,
		"moveMultiplier": number,
		"steeringEnabled": bool,
		"isTrainingLevel": bool,
		"functionDisableMask": number,
	},
	"levelId": any,
	"mapId": any,
	"bgmEvent": string,
	"mapData": {
		"map": arrayOf(arrayOf(number)),
		"tiles": arrayOf({
			"tileKey": oneOfType(['tileCorrosion', 'tileEnd', 'tileFloor', 'tileForbidden', 'tileRoad', 'tileStart', 'tileWall']),
			"heightType": number,
			"buildableType": number,
			"passableMask": number,
			"blackboard": arrayOf(_Blackboard)?,
			"effects": any,
		}),
		"blockEdges": any,
		"effects": any,
		"width": number,
		"height": number,
	},
	"tilesDisallowToLocate": arrayOf(any),
	"runes": any,
	"globalBuffs": any,
	"routes": arrayOf({
		"motionMode": number,
		"startPosition": _Position,
		"endPosition": _Position,
		"spawnRandomRange": _SpawnOffset,
		"spawnOffset": _SpawnOffset,
		"checkpoints": arrayOf({
		"type": number,
		"time": number,
		"position": _Position,
		"reachOffset": _SpawnOffset,
		"randomizeReachOffset": bool,
		"reachDistance": number,
	}),
		"allowDiagonalMove": bool,
		"visitEveryTileCenter": bool,
		"visitEveryNodeCenter": bool,
	}?),
	"enemies": arrayOf(any),
	"enemyDbRefs": arrayOf({
		"useDb": bool,
		"id": _Id,
		"level": number,
		"overwrittenData": {
			"name": _OverwrittenDataItem,
			"description": _OverwrittenDataItem,
			"prefabKey": _OverwrittenDataItem,
			"attributes": {
				"maxHp": _OverwrittenDataItem,
				"atk": _OverwrittenDataItem,
				"def": _OverwrittenDataItem,
				"magicResistance": _OverwrittenDataItem,
				"cost": _OverwrittenDataItem,
				"blockCnt": _OverwrittenDataItem,
				"moveSpeed": _OverwrittenDataItem,
				"attackSpeed": _OverwrittenDataItem,
				"baseAttackTime": _OverwrittenDataItem,
				"respawnTime": _OverwrittenDataItem,
				"hpRecoveryPerSec": _OverwrittenDataItem,
				"spRecoveryPerSec": _OverwrittenDataItem,
				"maxDeployCount": _OverwrittenDataItem,
				"massLevel": _OverwrittenDataItem,
				"baseForceLevel": _OverwrittenDataItem,
				"stunImmune": _OverwrittenDataItem,
				"silenceImmune": _OverwrittenDataItem,
			},
			"lifePointReduce": _OverwrittenDataItem,
			"rangeRadius": _OverwrittenDataItem,
			"talentBlackboard": any,
			"skills": any,
		}?,
	}),
	"waves": arrayOf({
		"preDelay": number,
		"postDelay": number,
		"maxTimeWaitingForNextWave": number,
		"fragments": arrayOf({
			"preDelay": number,
			"actions": arrayOf({
				"actionType": number,
				"managedByScheduler": bool,
				"key": _Id,
				"count": number,
				"preDelay": number,
				"interval": number,
				"routeIndex": number,
				"blockFragment": bool,
				"autoPreviewRoute": bool,
				"isUnharmfulAndAlwaysCountAsKilled": bool,
			}),
			"name": any,
		}),
		"name": any,
	}),
	"predefines": {
		"characterInsts": arrayOf(any),
		"tokenInsts": arrayOf(any),
		"characterCards": arrayOf(any),
		"tokenCards": arrayOf(any),
	},
	"excludeCharIdList": any,
	"randomSeed": number,
}
```
