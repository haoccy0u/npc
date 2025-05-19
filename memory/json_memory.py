from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from pathlib import Path

class JsonMemory:
    def __init__(self, npc_id: str = "default_npc"):
        self.npc_id = npc_id
        self.memory_file =Path("memory/memories.json")
        self.memories = self._load_memories()
        
    def _load_memories(self) -> Dict[str, Any]:
        """加载记忆数据"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                memories = json.load(f)
                return memories.get(self.npc_id, {})
        except Exception as e:
            print(f"加载记忆失败: {e}")
            return {}
            
    def _save_memories(self) -> None:
        """保存记忆数据"""
        try:
            # 先读取整个文件
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                all_memories = json.load(f)
            
            # 更新特定NPC的记忆
            all_memories[self.npc_id] = self.memories
            
            # 更新元数据
            self.memories["memory_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # 保存回文件
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(all_memories, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存记忆失败: {e}")
    
    def add_conversation(self, conversation: Dict[str, Any]) -> None:
        """添加对话记录到短期记忆
        
        Args:
            conversation: 包含对话信息的字典
        """
        self.memories["short_term_memory"]["recent_conversations"].append(conversation)
        self.memories["memory_metadata"]["total_conversations"] += 1
        self._save_memories()
    
    def update_current_context(self, context_update: Dict[str, Any]) -> None:
        """更新当前上下文
        
        Args:
            context_update: 要更新的上下文信息
        """
        self.memories["short_term_memory"]["current_context"].update(context_update)
        self._save_memories()
    
    def add_event(self, event: Dict[str, Any], importance: str = "normal") -> None:
        """添加事件到记忆
        
        Args:
            event: 事件信息
            importance: 重要程度 ("high"/"normal"/"low")
        """
        # 添加到最近事件
        self.memories["short_term_memory"]["recent_events"].append(event)
        
        # 如果是重要事件，也添加到长期记忆
        if importance == "high":
            self.memories["long_term_memory"]["important_events"].append(event)
        
        self.memories["memory_metadata"]["total_events"] += 1
        self._save_memories()
    
    def update_relationship(self, person_id: str, relationship_data: Dict[str, Any]) -> None:
        """更新与某人的关系
        
        Args:
            person_id: 对方的ID
            relationship_data: 关系数据
        """
        self.memories["long_term_memory"]["relationships"][person_id] = relationship_data
        self._save_memories()
    
    def add_experience(self, experience: Dict[str, Any], experience_type: str = "neutral") -> None:
        """添加个人经历
        
        Args:
            experience: 经历信息
            experience_type: 经历类型 ("positive"/"negative"/"neutral")
        """
        if experience_type in ["positive", "negative", "neutral"]:
            type_key = f"{experience_type}_experiences"
            self.memories["long_term_memory"]["personal_experiences"][type_key].append(experience)
            self._save_memories()
    
    def get_recent_conversations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最近的对话记录
        
        Args:
            limit: 返回的对话数量
            
        Returns:
            最近的对话列表
        """
        conversations = self.memories["short_term_memory"]["recent_conversations"]
        return conversations[-limit:]
    
    def get_current_context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        return self.memories["short_term_memory"]["current_context"]
    
    def get_relationship(self, person_id: str) -> Optional[Dict[str, Any]]:
        """获取与某人的关系信息
        
        Args:
            person_id: 对方的ID
            
        Returns:
            关系信息，如果不存在返回None
        """
        return self.memories["long_term_memory"]["relationships"].get(person_id)
    
    def get_all_memories(self) -> Dict[str, Any]:
        """获取所有记忆数据"""
        return self.memories 