# 国际象棋学习训练系统 - 设计文档

## 一、系统架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    国际象棋学习训练系统                        │
├─────────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    HTTP    ┌─────────────┐    UCI          │
│  │   前端      │ ←──────→ │   Flask    │ ←──────→ Stockfish │
│  │ (HTML/JS)   │    JSON    │   API      │    协议          │
│  └─────────────┘            └──────┬──────┘                 │
│                                    │                         │
│                                    ▼                         │
│                          ┌─────────────┐                     │
│                          │   文件存储  │                     │
│                          │ (JSON)     │                     │
│                          └─────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模块架构

| 模块 | 文件 | 职责 |
|------|------|------|
| **前端界面** | `webapp/index.html` | 界面展示（HTML骨架） |
| **后端API** | `webapp/app.py` | RESTful API服务 |
| **API封装** | `webapp/js/api.js` | HTTP请求封装 |
| **工具函数** | `webapp/js/utils.js` | 通用工具函数 |
| **棋盘训练器** | `webapp/js/chess-trainer.js` | 棋盘渲染、复盘演示、习题练习 |
| **导航系统** | `webapp/js/navigation.js` | 页面切换、导航状态管理 |
| **点评库页面** | `webapp/js/pages/library.js` | 棋局列表、添加演示棋局 |
| **棋手管理页面** | `webapp/js/pages/players.js` | 棋手CRUD操作 |
| **能力画像页面** | `webapp/js/pages/profile.js` | 画像生成与展示 |
| **训练计划页面** | `webapp/js/pages/plan.js` | 计划生成与展示 |
| **前端验证** | `webapp/js/validation.js` | 表单验证功能 |
| **后端测试** | `test_*.py` | 后端自动化测试 |
| **前端测试** | `webapp/test/frontend_tests.js` | 前端自动化测试 |

## 二、页面结构

### 2.1 导航结构

| 导航项 | 页面ID | 功能描述 |
|--------|--------|---------|
| 🏠 首页 | `page-home` | PGN加载、复盘演示、习题练习 |
| 📚 点评库 | `page-library` | 棋局存储、历史管理 |
| 👤 棋手管理 | `page-players` | 棋手档案管理 |
| 📊 能力画像 | `page-profile` | AI分析能力画像 |
| 📅 训练计划 | `page-plan` | 个性化训练计划 |

### 2.2 首页布局

```
┌─────────────────────────────────────────────────────────────┐
│  ♟️ 国际象棋学习训练系统  │  导航菜单                        │
├─────────────────────────────────────────────────────────────┤
│  文件选择区: [PGN下拉] [难度选择] [加载] [演示数据]         │
├─────────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────┐                    ┌─────────────────┐    │
│  │   复盘列表   │                    │     棋盘区域    │    │
│  │  • 5条失误  │                    │  • 8x8棋盘     │    │
│  │  • 进度状态  │                    │  • 播放控制    │    │
│  └─────────────┘                    └─────────────────┘    │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 分析面板: 错招 / 正招 / 战术解释                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                           │
│  [复盘] [习题] 标签切换 • 练习统计                        │
└─────────────────────────────────────────────────────────────┘
```

## 三、API接口设计

### 3.1 核心接口

| 模块 | 接口 | 方法 | 描述 |
|------|------|------|------|
| PGN分析 | `/api/analyze/<filename>` | GET | 分析PGN文件 |
| 复盘数据 | `/api/report/<filename>` | GET | 获取复盘数据 |
| 习题列表 | `/api/exercise/<filename>` | GET | 获取习题列表 |
| 走棋验证 | `/api/validate_move` | POST | 验证走法 |

### 3.2 点评库接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/library/games` | GET | 获取棋局列表 |
| `/api/library/game` | POST | 添加新棋局 |
| `/api/library/game/<id>` | GET | 获取单局详情 |
| `/api/library/game/<id>` | DELETE | 删除棋局 |

### 3.3 棋手管理接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/players` | GET | 获取棋手列表 |
| `/api/player` | POST | 创建新棋手 |
| `/api/player/<id>` | GET | 获取棋手详情 |
| `/api/player/<id>` | PUT | 更新棋手信息 |
| `/api/player/<id>` | DELETE | 删除棋手 |

### 3.4 能力画像接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/profile` | GET | 获取能力画像 |
| `/api/profile/generate` | POST | 生成能力画像 |
| `/api/profile/export` | GET | 导出画像JSON |

### 3.5 训练计划接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/training/plan` | GET | 获取训练计划 |
| `/api/training/plan/generate` | POST | 生成训练计划 |
| `/api/training/plan/export` | GET | 导出训练计划 |

### 3.6 训练闭环管控接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/training/task/complete` | POST | 完成任务，记录成绩 |
| `/api/training/progress` | GET | 获取训练进度概览 |
| `/api/training/progress/<player_id>` | GET | 获取指定选手训练进度 |
| `/api/training/reminders` | GET | 获取今日提醒 |
| `/api/training/reminders/<player_id>` | GET | 获取指定选手提醒 |
| `/api/training/summary/daily` | GET | 获取每日总结 |
| `/api/training/summary/weekly` | GET | 获取每周总结 |
| `/api/training/achievements` | GET | 获取成就列表 |
| `/api/training/achievements/<player_id>` | GET | 获取指定选手成就 |
| `/api/training/adjust` | POST | 触发计划调整 |

### 3.7 Token监控接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/token/status` | GET | 获取Token使用状态 |
| `/api/token/usage` | GET | 获取详细使用统计 |
| `/api/token/alerts` | GET | 获取告警列表 |
| `/api/token/config` | POST | 更新监控配置 |
| `/api/token/reset-circuit` | POST | 重置熔断器 |

## 四、数据结构设计

### 4.1 棋局数据

```json
{
    "game_id": "game_xxx",
    "filename": "test.pgn",
    "date": "2024-01-15",
    "white": "Player1",
    "black": "Player2",
    "result": "0-1",
    "pgn_content": "...",
    "mistakes": [
        {
            "step": 15,
            "loss": 250,
            "fen": "...",
            "actual_move": "e2e4",
            "best_move": "f2f3",
            "cause": "关键失误",
            "idea": "正确思路"
        }
    ],
    "total_mistakes": 5
}
```

### 4.2 棋手数据

```json
{
    "player_id": "player_xxx",
    "name": "张三",
    "nickname": "棋王",
    "level": "L3",
    "rating": 1800,
    "total_games": 50,
    "win_rate": 60,
    "game_history": ["game_001", "game_002"],
    "created_at": "2024-01-01",
    "updated_at": "2024-01-15"
}
```

### 4.3 能力画像数据

```json
{
    "player_id": "player_xxx",
    "player_name": "刘洪硕",
    "generated_at": "2026-04-28T23:01:25",
    "games_analyzed": 5,
    
    "overall_rating": 1620,
    "style": "进攻型",
    
    "detailed_analysis": {
        "opening": {
            "score": 52,
            "avg_mistakes": 1.2,
            "common_openings": ["意大利开局", "西班牙开局"],
            "suggestions": ["加强西西里防御应对", "丰富开局武器库"]
        },
        "tactics": {
            "score": 68,
            "total_tactical_mistakes": 8,
            "avg_loss": 185,
            "tactical_patterns": ["双攻", "牵制", "消除保护"]
        },
        "strategy": {
            "score": 48,
            "positional_errors": 12,
            "suggestions": ["改善兵结构评估", "加强计划制定"]
        },
        "endgame": {
            "score": 72,
            "endgame_mistakes": 3,
            "mastered_endgames": ["王兵残局", "车兵残局"]
        }
    },
    
    "strengths": [
        {"skill": "残局技巧", "score": 72, "evidence": "残局阶段失误率仅15%"},
        {"skill": "战术识别", "score": 68, "evidence": "成功发现80%的战术机会"}
    ],
    
    "weaknesses": [
        {"skill": "开局准备", "score": 52, "evidence": "前10步平均损失85cp"},
        {"skill": "局面判断", "score": 48, "evidence": "中局计划连贯性不足"}
    ],
    
    "trend_analysis": {
        "rating_trend": "上升",
        "improvement_rate": "+15分/周",
        "focus_areas": ["开局", "战略计划"]
    },
    
    "suggestions": [
        "建议重点加强西西里防御的学习",
        "每天进行30分钟战术训练，重点练习双攻和牵制",
        "增加慢棋对局数量，提高局面判断能力"
    ]
}
```

### 4.4 错题分类数据

```json
{
    "player_id": "player_xxx",
    "total_mistakes": 32,
    "mistake_distribution": {
        "tactical": {"count": 15, "percentage": 46.9, "avg_loss": 210},
        "strategic": {"count": 8, "percentage": 25.0, "avg_loss": 145},
        "opening": {"count": 5, "percentage": 15.6, "avg_loss": 95},
        "endgame": {"count": 4, "percentage": 12.5, "avg_loss": 180}
    },
    "tactical_breakdown": {
        "missed_threats": 6,
        "miscalculations": 5,
        "missed_opportunities": 4
    },
    "opening_breakdown": {
        "italian_opening": {"mistakes": 2, "avg_loss": 85},
        "spanish_opening": {"mistakes": 1, "avg_loss": 120},
        "sicilian_defense": {"mistakes": 2, "avg_loss": 80}
    },
    "frequency_by_move": {
        "1-10": {"count": 8, "percentage": 25},
        "11-25": {"count": 14, "percentage": 43.8},
        "26-40": {"count": 7, "percentage": 21.9},
        "41+": {"count": 3, "percentage": 9.3}
    },
    "top_mistakes": [
        {"fen": "...", "loss": 320, "category": "tactical"},
        {"fen": "...", "loss": 285, "category": "strategic"}
    ]
}
```

### 4.4 训练计划数据

```json
{
    "plan_id": "plan_xxx",
    "generated_at": "2024-01-15",
    "target_level": "L3",
    "target_rating": 1800,
    "short_term_goal": "1个月内提升战术计算能力",
    "long_term_goal": "3个月内达到棋协2级",
    "focus_areas": ["战术计算", "开局准备"],
    "daily_tasks": [
        {
            "name": "战术练习",
            "duration": "30分钟",
            "frequency": "每天",
            "description": "完成15道战术谜题",
            "completed": false,
            "streak": 0
        },
        {
            "name": "开局复习",
            "duration": "20分钟",
            "frequency": "每天",
            "completed": false,
            "streak": 0
        }
    ],
    "weekly_tasks": [
        {"name": "深度复盘", "duration": "2小时", "frequency": "每周"}
    ],
    "weekly_focus": "本周重点：战术训练",
    "recommendations": [
        {"resource": "《简明国际象棋教程》", "type": "书籍", "priority": "high"},
        {"resource": "Lichess战术训练", "type": "在线", "priority": "high"}
    ],
    "estimated_time": "3个月",
    "progress": 0,
    "completed_tasks": 0,
    "total_tasks": 120
}
```

### 4.5 Token使用数据

```json
{
    "total_calls": 580,
    "total_tokens": 156000,
    "last_updated": "2026-04-28T18:30:00",
    "daily": {
        "2026-04-26": {"calls": 45, "tokens": 12000},
        "2026-04-27": {"calls": 52, "tokens": 14500},
        "2026-04-28": {"calls": 38, "tokens": 10200}
    },
    "rpm": {
        "2026-04-28 18:25": 5,
        "2026-04-28 18:26": 8
    }
}
```

### 4.6 Token状态数据

```json
{
    "status": "normal",
    "daily_usage": 10200,
    "daily_limit": 100000,
    "daily_rate": 10.2,
    "monthly_usage": 36700,
    "monthly_limit": 2000000,
    "monthly_rate": 1.83,
    "total_calls": 580,
    "total_tokens": 156000,
    "current_rpm": 8,
    "rpm_limit": 60,
    "circuit_breaker_active": false,
    "circuit_breaker_resets_at": null
}
```

## 五、业务规则

| 规则编号 | 规则描述 |
|---------|---------|
| RULE-001 | 复盘演示最多展示5条失误（按失分降序） |
| RULE-002 | 必须完成复盘演示才能访问习题界面 |
| RULE-003 | 习题难度默认中级（失分≥150cp） |
| RULE-004 | 中级难度≥150cp，高级难度≥250cp |
| RULE-005 | 每天最多分析3盘棋 |
| RULE-006 | Token每日配额达到80%时触发警告 |
| RULE-007 | Token每日配额达到95%时触发熔断保护 |
| RULE-008 | 熔断保护持续5分钟后自动恢复 |
| RULE-009 | 请求速率超过60次/分钟时限流 |

## 六、文件存储结构

```
webapp/
├── app.py                    # Flask主应用
├── index.html                # 前端界面（HTML骨架）
├── js/
│   ├── api.js                # API调用封装
│   ├── utils.js              # 工具函数
│   ├── chess-trainer.js      # 棋盘训练器核心类
│   ├── navigation.js         # 导航系统
│   ├── validation.js         # 表单验证
│   └── pages/
│       ├── library.js        # 点评库页面
│       ├── players.js        # 棋手管理页面
│       ├── profile.js        # 能力画像页面
│       └── plan.js           # 训练计划页面
├── test/
│   ├── frontend_tests.js     # 前端测试
│   ├── enhanced_tests.js     # 增强前端测试
│   └── run_tests.js          # 测试运行器
├── tests/
│   ├── api.test.js           # API测试
│   ├── integration.test.js   # 集成测试
│   └── utils.js              # 测试工具
└── output/
    ├── learning_progress.json # 学习进度
    ├── token_usage.json       # Token使用记录
    ├── token_alerts.json      # Token告警记录
    ├── library/              # 点评库数据
    ├── players/              # 棋手档案
    ├── profiles/             # 能力画像
    ├── plans/                # 训练计划
    └── exercises/            # 错题练习数据
```

## 七、界面交互流程

### 7.1 学习流程

```
选择PGN文件 → 分析棋局 → 复盘演示 → 解锁习题 → 练习验证
```

### 7.2 画像生成流程

```
添加棋局 → 存入点评库 → 调用AI分析 → 生成能力画像 → 生成训练计划
```

### 7.3 导航流程

```
点击导航按钮 → 切换页面 → 加载数据 → 渲染内容
```

## 八、技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 前端框架 | HTML5 + JavaScript | - |
| CSS框架 | TailwindCSS | 3.x |
| 后端框架 | Flask | 2.x |
| 棋类引擎 | Stockfish | 16.x |
| 数据库 | 文件存储（JSON） | - |
| 测试框架 | pytest / Playwright | - |

## 九、模块依赖关系

| 模块 | 依赖模块 | 说明 |
|------|---------|------|
| `chess-trainer.js` | `api.js` | 调用API加载分析数据 |
| `navigation.js` | `pages/*.js` | 导航切换时加载页面数据 |
| `pages/library.js` | `api.js`, `utils.js` | API调用和加载状态 |
| `pages/players.js` | `api.js`, `utils.js` | API调用和加载状态 |
| `pages/profile.js` | `api.js`, `utils.js` | API调用和加载状态 |
| `pages/plan.js` | `api.js`, `utils.js` | API调用和加载状态 |
| `index.html` | 所有JS模块 | 按顺序引入 |