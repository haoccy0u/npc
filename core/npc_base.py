from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
import json
from .intent_service import IntentService

class ChannelType(Enum):
    FACE_TO_FACE = "face_to_face"
    SMS = "sms"
    FORUM = "forum"

@dataclass
class IdentityInfo:
    name: str
    race: str
    faction: str
    personality: Dict[str, float]  # 性格特征及其强度
    
@dataclass
class SocialRelation:
    target_id: str
    relationship_type: str
    trust_level: float
    familiarity: float

@dataclass
class EmotionalState:
    fear: float = 0.0
    trust: float = 0.0
    anger: float = 0.0
    joy: float = 0.0
    sadness: float = 0.0
    
class NPCBase:
    def __init__(self, intent_service: Optional[IntentService] = None):
        # 内部状态变量
        self._identityInfo: Optional[IdentityInfo] = None
        self._socialGraph: Dict[str, SocialRelation] = {}
        self._memoryStore: List[Dict] = []  # 预留接口，暂不实现具体功能
        self._goalState: str = ""
        self._emotionalState: EmotionalState = EmotionalState()
        self._currentIntent: Optional[Dict] = None
        self._currentOutput: Optional[str] = None
        self._channelAdapter: ChannelType = ChannelType.FACE_TO_FACE
        
        # 场景状态
        self._currentLocation: str = ""
        self._currentTime: str = ""
        self._nearbyEntities: List[Dict[str, Any]] = []
        self._environmentState: Dict[str, Any] = {}
        
        # 服务实例
        self._intentService = intent_service or IntentService()

    def initializeFromSources(self, npc_file: str, scene_file: str, npc_id: str = "merchant") -> None:
        """从配置文件初始化NPC
        
        Args:
            npc_file: NPC配置文件路径
            scene_file: 场景配置文件路径
            npc_id: NPC的ID，默认为"merchant"
        """
        try:
            # 加载NPC基础信息
            with open(npc_file, 'r', encoding='utf-8') as f:
                npc_data = json.load(f)
                if npc_id not in npc_data:
                    raise ValueError(f"在配置文件中未找到ID为 {npc_id} 的NPC")
                
                npc_info = npc_data[npc_id]
                if 'identity' not in npc_info:
                    raise ValueError(f"NPC {npc_id} 缺少 identity 信息")
                
                self._identityInfo = IdentityInfo(**npc_info['identity'])
                self._goalState = npc_info.get('initial_goal', '')
                
            # 加载场景社交关系
            with open(scene_file, 'r', encoding='utf-8') as f:
                scene_data = json.load(f)
                for relation in scene_data.get('social_relations', []):
                    relation_obj = SocialRelation(**relation)
                    self._socialGraph[relation_obj.target_id] = relation_obj
                    
        except FileNotFoundError as e:
            raise FileNotFoundError(f"配置文件不存在: {str(e)}")
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {str(e)}")
        except Exception as e:
            raise Exception(f"初始化NPC时出错: {str(e)}")

    def setChannel(self, channel_type: ChannelType) -> None:
        """设置当前交互通道类型"""
        self._channelAdapter = channel_type

    def getChannelProfile(self) -> Dict[str, Any]:
        """返回当前通道的行为风格和响应限制"""
        # 预留接口，返回默认值
        return {
            "style": "normal",
            "response_limit": None
        }

    def adaptResponseStyle(self, output: str) -> str:
        """根据当前通道调整输出风格"""
        # 预留接口，暂时直接返回原始输出
        return output

    def toNPCSnapshot(self) -> Dict[str, Any]:
        """打包NPC当前状态为快照"""
        return {
            "identity": asdict(self._identityInfo) if self._identityInfo else {},
            "emotional_state": asdict(self._emotionalState),
            "current_goal": self._goalState,
            "social_context": [asdict(rel) for rel in self._socialGraph.values()],
            "memory_content": self._memoryStore,
            "channel_type": self._channelAdapter.value
        }
        
    def toSceneSnapshot(self) -> Dict[str, Any]:
        """打包当前场景状态为快照"""
        # 确保 last_intent 和 last_output 是可序列化的
        #last_intent = self._currentIntent
        #if isinstance(last_intent, (dict, list, str, int, float, bool, type(None))):
        #    last_intent_safe = last_intent
        #else:
        #    last_intent_safe = str(last_intent) if last_intent is not None else None
            
       # last_output = self._currentOutput
       # if isinstance(last_output, (dict, list, str, int, float, bool, type(None))):
       #     last_output_safe = last_output
       # else:
       #     last_output_safe = str(last_output) if last_output is not None else None
            
        return {
            "location": self._currentLocation,
            "time": self._currentTime,
            "nearby_entities": self._nearbyEntities,
            "environment_state": self._environmentState,
            "current_channel": self._channelAdapter.value,
            "last_intent": self._currentIntent,
            "last_output": self._currentOutput,
        }

    async def evaluateIntent(self) -> Dict[str, Any]:
        """生成当前状态下的行为意图
        
        Returns:
            意图对象
        """
        # 获取当前状态快照
        npc_snapshot = self.toNPCSnapshot()
        scene_snapshot = self.toSceneSnapshot()
        
        # 调用意图服务生成意图
        intent = await self._intentService.evaluate(
            npc_snapshot=npc_snapshot,
            scene_snapshot=scene_snapshot
        )
        
        # 缓存当前意图
        self._currentIntent = intent
        return intent

    def generateResponse(self) -> str:
        """基于当前意图生成响应"""
        # 预留接口，将在OutputService中实现具体逻辑
        pass

    def updateMemory(self, event: Dict[str, Any]) -> None:
        """更新记忆
        
        Args:
            event: 需要记录的事件
        """
        # 预留接口，暂时只保存事件
        self._memoryStore.append(event)

    def getStatus(self) -> Dict[str, Any]:
        """获取当前状态摘要"""
        return {
            "identity": self._identityInfo,
            "current_goal": self._goalState,
            "emotional_state": self._emotionalState,
            "current_channel": self._channelAdapter.value,
            "current_location": self._currentLocation,
            "current_time": self._currentTime
        }

    def debugTrace(self) -> Dict[str, Any]:
        """输出完整的状态和行为路径"""
        return {
            "npc_state": self.toNPCSnapshot(),
            "scene_state": self.toSceneSnapshot()
        } 