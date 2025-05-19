from typing import Dict, Any, Optional
from .llm_service import LLMService
from langchain_openai import ChatOpenAI
import json

class IntentService(LLMService):
    # 意图生成的提示模板
    INTENT_PROMPT = """基于以下信息，分析NPC当前的意图：
    
    NPC基本信息：{identity}
    当前情感状态：{emotional_state}
    当前目标：{current_goal}
    社交关系：{social_context}
    历史记忆：{memory_content}
    通信通道：{channel_type}
    
    场景信息：
    当前位置：{location}
    当前时间：{time}
    周围实体：{nearby_entities}
    环境状态：{environment_state}
    当前通道：{current_channel}
    上一个意图：{last_intent}
    上一次输出：{last_output}
    
    请基于NPC的性格特征、历史记忆、当前状态和场景信息，分析其最可能的意图和情感状态。
    输出格式要求：
    {{
        "intent_type": "意图类型，如deflect/attack/agree等",
        "intent_description": "具体意图描述",
        "emotion": "情感状态",
        "target": "意图针对的对象",
        "confidence": "置信度0-1",
        "reasoning": "推理过程"
    }}
    """

    def __init__(self, llm: Optional[ChatOpenAI] = None):
        """初始化意图服务
        
        Args:
            llm: LLM模型实例
        """
        # 调用父类初始化
        super().__init__(llm)
        
        # 创建意图Chain
        self.intent_chain = self.create_chain(self.INTENT_PROMPT)

    async def evaluate(
        self,
        npc_snapshot: Dict[str, Any],
        scene_snapshot: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估当前情境并生成意图
        
        Args:
            npc_snapshot: NPC当前状态快照，包含：
                - identity: Dict, NPC身份信息
                - emotional_state: Dict, 情感状态
                - current_goal: str, 当前目标
                - social_context: List, 社交关系
                - memory_content: List, 历史记忆
            scene_snapshot: 场景状态快照，包含：
                - location: str, 当前位置
                - time: str, 当前时间
                - nearby_entities: List, 周围实体
                - environment_state: Dict, 环境状态
            
        Returns:
            Dict包含意图分析结果
        """
        try:
            # 合并两个快照的数据
            intent_inputs = {**npc_snapshot, **scene_snapshot}
            
            # 生成意图
            intent_analysis = await self.generate_response(
                self.intent_chain,
                intent_inputs
            )
            
            return intent_analysis
            
        except Exception as e:
            print(f"生成意图时出错: {str(e)}")
            return {
                "error": str(e),
                "intent_type": "error",
                "intent_description": "意图生成失败",
                "confidence": 0
            } 