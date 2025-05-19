# NPC

## 概述
这是一个基于智能交互的 NPC（非玩家角色）系统，通过模块化设计实现了复杂的 NPC 行为模拟和交互响应。系统能够让 NPC 具备情感状态、社交关系以及动态的行为决策能力。

## 架构

### NPCBase（NPC 实例对象）
npc的基类

#### 内部状态 (Internal State)
```
├── #region Internal State（私有状态变量）
│   ├──  _identityInfo              // 永久性设定（姓名、种族、派系、性格等）
│   ├──  _socialGraph               // 社会关系图谱（来自场景设定）
│   ├──  _memoryStore               // 互动生成的记忆记录（语言、行为、信任变动等）
│   ├──  _goalState                 // 当前动因、长期目标（可静态设定或动态推导）
│   ├──  _emotionalState            // 情绪状态（恐惧、信任、愤怒等）
│   ├──  _currentIntent             // 当前行为意图缓存（由 IntentService 提供）
│   ├──  _currentOutPut             // 当前输出（由 OutputService 提供）
│   └──  _channelAdapter            // 当前交互通道策略器（面对面/短信/论坛）
```

#### 初始化方法 (Initialization)
```
├── #region Initialization
│   ├──  initializeFromSources(npcFile, sceneFile)
│       → 从 NPC 数据文件加载 identity 与初始状态
│       → 从场景文件加载关系图谱与局部动态
│       → 可拓展支持互动中派生状态补充（如首次相遇记录）
│       → 当前预留结构，加载机制与顺序待设计完善
```

#### 通道适配器 (Channel Adapter)
```
├── #region Channel Adapter
│   ├──  setChannel(type)               // 设置当前交互通道类型（三种分别是面对面，短信和网络论坛）
这部分暂时不用实现具体功能，仅占位

```

#### 行为接口 (Behavior Interface)
```
├── #region Behavior Interface
│   ├──  toSnapshot()                   // 打包当前状态为 npcSnapshot（供服务使用）
│   ├──  evaluateIntent(context)        // 通过 IntentService 生成并缓存行为意图
│   ├──  generateResponse()             // 通过 OutputService 基于意图生成语言/行为
│   ├──  updateMemory(event)            // 将行为结果写入记忆，影响后续状态
│   ├──  getStatus()                    // 获取当前状态摘要（供系统/玩家观察）
│   └──  debugTrace()                   // 输出完整状态与行为路径（开发调试）
```

### IntentService（行为意图服务）
负责生成 NPC 的行为意图。

```
IntentService（行为意图服务模块）
├──  evaluate(npcSnapshot, context)
│     → 调用llm返回意图对象（返回一段包涵npc意图的文本（描述性质的）涵盖意图的要素如 type: "deflect", emotion: "tense", target: "player"）
├──  injectBehaviorRules(profile)
│     → 加载不同行为模型（如谨慎型、攻击型等）
├──  batchEvaluate(npcSnapshots[])
│     → 支持多个 NPC 的并发意图计算
```

### OutputService（输出生成服务）
负责将意图转化为具体的输出响应。

```
OutputService（输出生成服务模块）
├──  generateDialogue(intent, npcSnapshot，_channelAdapter)
│     → 基于意图与通道调用llm生成语言响应（文本 + 标签）
├──  executeAction(intent, npcSnapshot)
│     → 输出非语言行为（行动、通报、退出等）
├──  applyExpressionStyle(intent, emotion)
│     → 决定语言风格（如挑衅、模糊、激动）
├──  batchRespond(intentList, npcSnapshots)
│     → 并发输出优化（提升响应效率）
```

## 文件结构

```
npc/
├── core/
│   ├── npc_base.py           # NPCBase 核心实现
│   ├── intent_service.py     # 意图服务实现
│   └── output_service.py     # 输出服务实现
├── config/
│   ├── npc_configs/         # NPC 配置文件
│   └── channel_configs/     # 通道配置文件
└── README.md
```

## 使用流程

1. 创建 NPC 配置文件
2. 设置适当的通道适配器
3. 通过行为接口进行交互
4. 监控和调试 NPC 状态

## todo

1. 完善情感和社会关系系统
2. 实现记忆系统接口
3. 优化多 NPC 并发处理
4. 添加更多行为模型支持
5. 改进调试和监控工具