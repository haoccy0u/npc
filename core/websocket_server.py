import asyncio
import websockets
import json
from typing import Dict, Any, Optional
from .llm_service import LLMService, log_message

class WebSocketServer:
    def __init__(self, llm_service: LLMService, host: str = "localhost", port: int = 8080):
        self.llm_service = llm_service
        self.host = host
        self.port = port
        self.connections = set()
        self.on_client_connected = None  # 添加回调属性
        
    async def handle_client(self, websocket):
        """处理单个客户端连接"""
        try:
            self.connections.add(websocket)
            log_message(f"新的客户端连接")
            
            # 调用连接回调发送寒暄消息
            if self.on_client_connected:
                try:
                    log_message("发送寒暄消息...")
                    await self.on_client_connected(websocket)
                    log_message("寒暄消息已发送")
                except Exception as e:
                    log_message(f"发送寒暄消息时出错: {str(e)}", "ERROR")
            
            async for message in websocket:
                try:
                    # 解析接收到的消息
                    data = json.loads(message)
                    
                    # 根据消息类型处理
                    if data.get("type") == "dialogue":
                        # 使用LLM服务生成响应
                        response = await self._handle_dialogue(data)
                        # 发送响应
                        await websocket.send(json.dumps(response))
                    else:
                        log_message(f"未知的消息类型: {data.get('type')}", "WARNING")
                        
                except json.JSONDecodeError:
                    log_message(f"无效的JSON格式: {message}", "ERROR")
                except Exception as e:
                    log_message(f"处理消息时出错: {str(e)}", "ERROR")
                    
        except websockets.exceptions.ConnectionClosed:
            log_message("客户端断开连接")
        finally:
            self.connections.remove(websocket)
    
    async def _handle_dialogue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理对话消息"""
        try:
            # 这里需要根据你的LLM服务具体实现来调用
            chain = self.llm_service.create_chain("你的提示模板")
            result = await self.llm_service.generate_response(chain, data)
            
            # 构造返回消息
            return {
                "type": "dialogue",
                "speaker": "AI",  # 或从result中获取
                "content": result.get("response", ""),  # 根据实际响应格式调整
                "is_player": False
            }
        except Exception as e:
            log_message(f"处理对话消息时出错: {str(e)}", "ERROR")
            return {
                "type": "error",
                "content": f"处理消息时出错: {str(e)}"
            }
    
    async def start(self):
        """启动WebSocket服务器"""
        try:
            server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            log_message(f"WebSocket服务器启动在 ws://{self.host}:{self.port}")
            await server.wait_closed()
        except Exception as e:
            log_message(f"启动WebSocket服务器时出错: {str(e)}", "ERROR")
