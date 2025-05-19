import asyncio
from core.npc_base import NPCBase, EmotionalState
from langchain_openai import ChatOpenAI
import json

async def main():
    # 创建一个商人NPC实例
    merchant = NPCBase()
    
    # 初始化NPC
    merchant.initializeFromSources(
        "config/npc_configs/default_npcs.json",
        "config/scene_configs/market_scene.json",
    )
    
    # 设置当前情感状态
    merchant._emotionalState = EmotionalState(
        joy=0.7,  # 心情不错
        trust=0.6,  # 比较信任
        fear=0.2,  # 略有担忧
        anger=0.1   # 很少生气
    )
    
    # 更新场景状态
    merchant._currentLocation = "繁华市场"
    merchant._currentTime = "上午"
    merchant._nearbyEntities = [
        {
            "id": "player",
            "type": "player",
            "name": "玩家",
            "distance": "近",
            "behavior": "正在查看商品"
        },
        {
            "id": "guard_1",
            "type": "guard",
            "name": "卫兵",
            "distance": "远",
            "behavior": "巡逻中"
        }
    ]
    merchant._environmentState = {
        "weather": "晴朗",
        "crowd_level": "热闹",
        "business_status": "良好"
    }
    
    # 生成意图
    intent = await merchant.evaluateIntent()
    
    # 打印结果
    print("\n=== NPC状态 ===")
    print(json.dumps(merchant.toNPCSnapshot(), indent=2, ensure_ascii=False))
    print("\n=== 场景状态 ===")
    print(json.dumps(merchant.toSceneSnapshot(), indent=2, ensure_ascii=False))
    print("\n=== 生成的意图 ===")
    print(json.dumps(intent, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main()) 