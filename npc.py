import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import json
import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from intent_module import IntentProcessor
from memory.json_memory import JsonMemory

# LLM配置
LLM_MODEL = "gpt-4o"  # 修正模型名称
LLM_BASE_URL = "https://api.ifopen.ai/v1"
LLM_API_KEY = "sk-SdjbKZ455Psww0ZoKvSl4as8dKai9i3CUQWikdz4w2QBA4Vq"

class NPC:
    def __init__(
        self,
        npc_id: str = "default_npc",
        api_key: Optional[str] = None
    ):
        """初始化NPC
        
        Args:
            npc_id: NPC的唯一标识符
            api_key: OpenAI API密钥（可选，默认使用环境变量）
        """
        self.npc_id = npc_id
        
        # 设置API密钥
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", LLM_API_KEY)
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model_name=LLM_MODEL,
            openai_api_base=LLM_BASE_URL,
            openai_api_key=self.api_key,
            temperature=0.7
        )
        
        # 加载NPC配置
        self.config = self._load_npc_config()
        
        # 初始化记忆系统
        self.memory = JsonMemory(npc_id=npc_id)
        
        # 初始化意图处理器，传入配置好的LLM
        self.intent_processor = IntentProcessor(
            llm=self.llm,
            npc_id=npc_id,
            npc_config=self.config
        )
        
        print(f"已初始化NPC: {npc_id}, 使用模型: {LLM_MODEL}")
        
    def _load_npc_config(self) -> Dict[str, Any]:
        """加载NPC配置"""
        config_path = Path("config/npc_configs/default_npcs.json")  # 修改路径
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                configs = json.load(f)
                return configs.get(self.npc_id, configs["default_npc"])
        except Exception as e:
            print(f"加载NPC配置失败: {e}")
            return {}
            
    async def process_input(
        self,
        user_input: str,
        user_id: str = "user"
    ) -> Dict[str, Any]:
        """处理用户输入
        
        Args:
            user_input: 用户输入的文本
            user_id: 用户ID
            
        Returns:
            Dict包含NPC的响应信息
        """
        try:
            # 记录对话
            conversation = {
                "time": datetime.now().isoformat(),
                "speaker": user_id,
                "content": user_input,
                "type": "input"
            }
            self.memory.add_conversation(conversation)
            
            # 生成意图和策略
            response = await self.intent_processor.process_intent(
                current_context=user_input,
                target_id=user_id
            )
            
            # 记录NPC响应
            npc_response = {
                "time": datetime.now().isoformat(),
                "speaker": self.npc_id,
                "content": str(response),
                "type": "response",
                "intent": response["intent_analysis"],
                "strategy": response["selected_strategy"]
            }
            self.memory.add_conversation(npc_response)
            
            return response
        except Exception as e:
            print(f"处理输入时出错: {str(e)}")
            return {
                "intent_analysis": {"error": str(e)},
                "selected_strategy": {"error": str(e)}
            }

async def test_npc():
    """测试NPC功能"""
    # 创建NPC实例
    npc = NPC(npc_id="default_npc")
    
    # 测试对话
    test_inputs = [
        "今天天气真不错，想出去走走吗？",
    ]
    
    for user_input in test_inputs:
        print("\n用户输入:", user_input)
        try:
            response = await npc.process_input(user_input)
            print("\nNPC意图分析:", json.dumps(response["intent_analysis"], ensure_ascii=False, indent=2))
            print("\n选择的策略:", json.dumps(response["selected_strategy"], ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"\n处理输入时出错: {e}")
        print("\n" + "="*50)

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_npc()) 