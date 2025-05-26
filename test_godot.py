import asyncio
import os
from core.llm_service import LLMService
from core.websocket_server import WebSocketServer
import json
import time

# 测试用的寒暄消息
TEST_GREETING = {
    "type": "dialogue",
    "speaker": "商人",
    "content": "欢迎光临！我是这里的商人。今天想看些什么？",
    "is_player": False
}

# 对话提示模板
DIALOGUE_TEMPLATE = """你是一个商人NPC，正在与玩家进行对话。
请根据玩家的输入生成合适的回复。
玩家说: {content}

请用JSON格式回复，包含以下字段：
- speaker: 你的名字（商人）
- content: 你的回复内容

要求：
1. 保持对话的连贯性
2. 回复要简洁自然
3. 符合商人的身份特征
"""

class DialogueService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.dialogue_chain = llm_service.create_chain(DIALOGUE_TEMPLATE)
        self.has_greeted = False
        self.message_count = 0
        self.start_time = time.time()
    
    async def handle_connection(self, websocket) -> None:
        """处理新的连接，发送寒暄消息"""
        print("\n=== 新客户端连接，发送寒暄消息 ===")
        print(f"发送者: {TEST_GREETING['speaker']}")
        print(f"内容: {TEST_GREETING['content']}")
        print("===================\n")
        
        # 实际发送寒暄消息
        greeting_json = json.dumps(TEST_GREETING)
        await websocket.send(greeting_json)
    
    async def handle_message_received(self, message: str, websocket) -> None:
        """处理接收到的消息"""
        print(f"\n收到消息: {message}\n")
    
    async def handle_dialogue(self, message: str) -> dict:
        """处理对话消息并返回响应"""
        try:
            # 准备输入数据
            inputs = {
                "content": message
            }
            
            # 获取AI响应
            result = await self.llm_service.generate_response(
                self.dialogue_chain, 
                inputs
            )
            
            # 构造返回消息
            return {
                "type": "dialogue",
                "speaker": result.get("speaker", "商人"),
                "content": result.get("content", ""),
                "is_player": False
            }
        except Exception as e:
            print(f"处理对话时出错: {str(e)}")
            return {
                "type": "error",
                "content": f"对话生成失败: {str(e)}"
            }

async def main():
    try:
        # 初始化LLM服务
        api_key = "sk-SdjbKZ455Psww0ZoKvSl4as8dKai9i3CUQWikdz4w2QBA4Vq"
        if not api_key:
            print("错误: 未设置OPENAI_API_KEY环境变量")
            return
            
        llm_service = LLMService(api_key=api_key)
        print("LLM服务初始化成功")
        
        # 创建对话服务
        dialogue_service = DialogueService(llm_service)
        
        # 创建并配置WebSocket服务器
        server = WebSocketServer(
            llm_service=llm_service,
            host="localhost",
            port=8080
        )
        
        # 替换服务器的对话处理方法
        server._handle_dialogue = dialogue_service.handle_dialogue
        # 添加连接处理方法
        server.on_client_connected = dialogue_service.handle_connection
        # 添加消息接收处理方法
        server.on_message_received = dialogue_service.handle_message_received
        
        print("\n=== AI对话服务已启动 ===")
        print("WebSocket服务器运行在 ws://localhost:8080")
        print("等待Godot客户端连接...")
        print("\n提示：")
        print("1. 在Godot中运行对话场景")
        print("2. 在对话框中输入消息")
        print("3. 等待AI响应")
        print("\n按Ctrl+C停止服务器")
        
        # 启动服务器
        await server.start()
        
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
