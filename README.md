# NPC 智能交互系统

[前面的系统架构部分保持不变...]

## 简化文件结构

```
npc/
├── config/
│   ├── npc_configs/           # NPC预制配置文件
│   │   └── default_npcs.json  # 默认NPC配置
│   └── strategy_configs/      # 策略配置文件
│       └── expression_strategies.json  # 表达策略配置
├── memory/
│   └── memory_base.py        # 基础记忆系统（使用预制配置）
├── intent_module.py          # 整合的意图处理模块
├── output_module.py          # 整合的输出处理模块
├── strategy.py              # 可配置的策略系统
├── npc.py                   # NPC主类实现
└── README.md

```

## 实现优先级

### 1. 配置系统
- 设计 NPC 配置格式（包含永久记忆、初始关系等）
- 设计表达策略配置格式（定义不同类型的表达方式）

### 2. 核心模块实现


3. **intent_module.py**
   - 整合情境感知、状态评估、目标动因和意图判断
   - 基于当前状态生成行为意图，注意，这一步需要调用llm来生成
   - 提供统一的意图生成接口

4. **output_module.py**
   - 整合语言生成和行为决策
   - 根据策略配置生成响应
   - 提供统一的输出生成接口

