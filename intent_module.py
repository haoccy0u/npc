from typing import Dict, Any, Optional
import json
import os
from pathlib import Path
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.schema import BaseMemory
from memory.json_memory import JsonMemory

class IntentProcessor:
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        memory: Optional[BaseMemory] = None,
        npc_config: Optional[Dict[str, Any]] = None,
        strategy_config: Optional[Dict[str, Any]] = None,
        npc_id: str = "default_npc"
    ):
        self.llm = llm or ChatOpenAI()
        self.memory = memory
        self.npc_id = npc_id
        self.json_memory = JsonMemory(npc_id=npc_id)
        
        # 加载配置
        self.npc_config = npc_config or self.load_npc_config()
        self.strategy_config = strategy_config or self.load_strategy_config()
        
        # 意图生成的提示模板
        self.intent_prompt = ChatPromptTemplate.from_template(
            """基于以下信息，分析NPC当前的意图：
            
            NPC基本信息：{npc_info}
            历史记忆信息：{memory_content}
            当前上下文：{current_context}
            最近对话历史：{recent_conversations}
            重要关系信息：{relationships}
            
            请基于NPC的性格特征、历史记忆和当前状态，分析其最可能的意图和情感状态。
            输出格式要求：
            {{
                "intent": "具体意图描述",
                "emotion": "情感状态",
                "confidence": "置信度0-1",
                "reasoning": "推理过程"
            }}
            """
        )
        
        # 策略匹配的提示模板
        self.strategy_prompt = ChatPromptTemplate.from_template(
            """基于以下信息，选择最合适的响应策略：
            
            当前意图：{intent}
            当前上下文：{current_context}
            NPC当前状态：{npc_state}
            可用表达策略：{expression_strategies}
            对方关系信息：{target_relationship}
            
            请选择一个最合适的策略ID和表达方式。
            输出格式要求：
            {{
                "strategy_id": "选择的策略ID",
                "expression_type": "选择的表达类型(happy/neutral/sad)",
                "context_type": "场景类型(formal/casual/intimate)",
                "reason": "选择原因"
            }}
            """
        )
        
        # 创建两个Chain
        self.intent_chain = LLMChain(
            llm=self.llm,
            prompt=self.intent_prompt,
            output_key="intent_analysis"
        )
        
        self.strategy_chain = LLMChain(
            llm=self.llm,
            prompt=self.strategy_prompt,
            output_key="strategy_selection"
        )

    @staticmethod
    def load_npc_config(npc_id: str = "default_npc") -> Dict[str, Any]:
        """加载NPC配置
        
        Args:
            npc_id: NPC的标识符，默认使用default_npc
            
        Returns:
            Dict包含NPC的配置信息
        """
        config_path = Path("config/npc_configs/default_npcs.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                configs = json.load(f)
                return configs.get(npc_id, configs["default_npc"])
        except Exception as e:
            print(f"加载NPC配置失败: {e}")
            return {}

    @staticmethod
    def load_strategy_config() -> Dict[str, Any]:
        """加载表达策略配置
        
        Returns:
            Dict包含表达策略配置信息
        """
        config_path = Path("config/strategy_configs/expression_strategies.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载策略配置失败: {e}")
            return {}

    @staticmethod
    def _clean_and_parse_json(json_str: str) -> Dict[str, Any]:
        """清理并解析JSON字符串
        
        Args:
            json_str: 要解析的JSON字符串
            
        Returns:
            解析后的字典
        """
        try:
            # 移除可能的Markdown代码块标记
            json_str = json_str.replace('```json', '').replace('```', '')
            
            # 清理字符串
            json_str = json_str.strip()
            
            # 找到第一个{和最后一个}之间的内容
            start = json_str.find('{')
            end = json_str.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = json_str[start:end]
            
            # 尝试解析JSON
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"\nJSON解析失败: {e}")
            print(f"原始字符串: {json_str}")
            return {}

    async def process_intent(
        self,
        current_context: str,
        target_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """处理意图并选择策略
        
        Args:
            current_context: 当前对话上下文
            target_id: 交互目标的ID（如果有）
            
        Returns:
            Dict包含选择的策略ID和相关信息
        """
        try:
            # 获取记忆内容
            memory_content = self.memory.load_memory_variables({}) if self.memory else {}
            
            # 获取JSON记忆内容
            recent_conversations = self.json_memory.get_recent_conversations(limit=5)
            current_memory_context = self.json_memory.get_current_context()
            target_relationship = self.json_memory.get_relationship(target_id) if target_id else None
            
            # 第一步：生成意图
            intent_result = await self.intent_chain.ainvoke({
                "npc_info": self.npc_config.get("basic_info", {}),
                "memory_content": memory_content,
                "current_context": current_context,
                "recent_conversations": recent_conversations,
                "relationships": target_relationship
            })
            
            print("\n=== 意图生成原始结果 ===")
            print(f"类型: {type(intent_result)}")
            print(f"内容: {intent_result}")
            
            # 解析意图结果
            intent_analysis = intent_result.get("intent_analysis", intent_result)
            if isinstance(intent_analysis, str):
                intent_analysis = self._clean_and_parse_json(intent_analysis)
                if not intent_analysis:
                    intent_analysis = {
                        "intent": "解析失败",
                        "emotion": "neutral",
                        "confidence": 0,
                        "reasoning": "JSON解析错误"
                    }
            
            # 第二步：匹配策略
            strategy_result = await self.strategy_chain.ainvoke({
                "intent": intent_analysis,
                "current_context": current_context,
                "npc_state": self.npc_config.get("initial_state", {}),
                "expression_strategies": self.strategy_config.get("emotion_expression_strategies", {}),
                "target_relationship": target_relationship
            })
            
            print("\n=== 策略生成原始结果 ===")
            print(f"类型: {type(strategy_result)}")
            print(f"内容: {strategy_result}")
            
            # 解析策略结果
            strategy_selection = strategy_result.get("strategy_selection", strategy_result)
            if isinstance(strategy_selection, str):
                strategy_selection = self._clean_and_parse_json(strategy_selection)
                if not strategy_selection:
                    strategy_selection = {
                        "strategy_id": "default",
                        "expression_type": "neutral",
                        "context_type": "casual",
                        "reason": "JSON解析错误"
                    }
            
            # 更新记忆
            self.json_memory.update_current_context({
                "current_topic": current_context,
                "emotional_state": intent_analysis.get("emotion", "neutral")
            })
            
            return {
                "intent_analysis": intent_analysis,
                "selected_strategy": strategy_selection
            }
        except Exception as e:
            print(f"\n处理意图时出错: {str(e)}")
            print(f"错误类型: {type(e)}")
            import traceback
            print(f"错误堆栈: {traceback.format_exc()}")
            return {
                "intent_analysis": {"error": str(e)},
                "selected_strategy": {"error": str(e)}
            } 