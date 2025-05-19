from typing import Dict, Any, Optional
import os
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from operator import itemgetter
import json

# 默认配置
LLM_MODEL = "gpt-4o"
LLM_BASE_URL = "https://api.ifopen.ai/v1"
LLM_API_KEY = None  # 默认为 None，将从环境变量获取

def log_message(message: str, level: str = "INFO"):
    """简单的日志记录函数"""
    print(f"[{level}] {message}")

class LLMService:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        """初始化LLM服务
        
        Args:
            api_key: OpenAI API密钥，如果不提供则从环境变量获取
            base_url: API基础URL，如果不提供则使用默认值
            model: 模型名称，如果不提供则使用默认值
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", LLM_API_KEY)
        self.base_url = base_url or LLM_BASE_URL
        self.model = model or LLM_MODEL
        
        if not self.api_key:
            raise ValueError("未提供 API 密钥，请通过参数传入或设置 OPENAI_API_KEY 环境变量")
            
        self.llm = ChatOpenAI(
            model=self.model,
            base_url=self.base_url,
            api_key=self.api_key
        )
        
        log_message(f"已初始化 LLMService，使用模型: {self.model}", "INFO")
    
    def create_chain(self, prompt_template: str):
        """创建处理链
        
        Args:
            prompt_template: 提示模板字符串
            
        Returns:
            Runnable chain实例，可以直接调用或与其他组件组合
        """
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # 创建基本的处理链
        chain = (
            RunnablePassthrough() | prompt | self.llm
        )
        
        return chain
    
    @staticmethod
    def clean_and_parse_json(json_str: str) -> Dict[str, Any]:
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
            print(f"JSON解析失败: {e}")
            print(f"原始字符串: {json_str}")
            return {}
            
    async def generate_response(self, chain, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """生成响应
        
        Args:
            chain: Runnable chain实例
            inputs: 输入参数字典
            
        Returns:
            处理后的响应字典
        """
        try:
            result = await chain.ainvoke(inputs)
            
            # 如果结果是 AIMessage 对象，获取其内容
            if hasattr(result, 'content'):
                result = result.content
            
            # 如果输出是字符串，尝试解析JSON
            if isinstance(result, str):
                result = self.clean_and_parse_json(result)
            
            return result
        except Exception as e:
            print(f"生成响应时出错: {str(e)}")
            return {"error": str(e)} 