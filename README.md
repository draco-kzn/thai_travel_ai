# Thailand Travel Simulator

一个用 Streamlit 做出来的 AI 驱动旅行模拟小游戏：你从泰国某座城市落地，带着有限预算和体力，在天气、时间、路线和住宿成本的限制下规划一段“穷游 / 特种兵 / 度假混合体”旅程。

An AI-powered Thailand travel sim built with Streamlit. You choose a starting city, budget, month, and arrival time, then survive the trip by balancing money, stamina, weather, transport, and hotel choices.

这个项目很典型地属于 `vibe coding` 原型：
- 有明确的玩法闭环
- 有很强的视觉氛围
- 有 AI 生成内容参与体验
- 代码量不大，适合继续快速迭代

## Demo 亮点

- `10` 座泰国城市可选，覆盖城市、海岛和夜生活路线
- AI 根据 `城市 + 月份` 生成天气概率
- AI 根据 `城市 + 天气 + 时间段` 生成场景图
- 不同城市自动切换 BGM
- 预算、体力、时间、住宿共同约束行动
- 支持白天 / 夜晚活动和交通规则差异
- 旅行结束时生成 AI 结算纪念图

## Tech Stack

- `Python`
- `Streamlit`
- `ZhipuAI / GLM`
- `python-dotenv`

## 项目结构

```text
.
├─ app.py           # Streamlit UI、视觉层、页面流程
├─ game_state.py    # 游戏状态、行动/睡眠/移动/结算逻辑
├─ data_store.py    # 城市数据、活动列表、交通矩阵、价格倍率
├─ ai_manager.py    # AI 天气、AI 图片、BGM 封装
├─ requirements.txt
└─ .env.example
```

## 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，然后填入你的智谱 API Key：

```env
ZHIPUAI_API_KEY=your_api_key_here
```

如果你不配 Key，项目依然可以启动，但会退化为默认天气概率和默认图片，AI 体验不完整。

### 3. 启动项目

```bash
streamlit run app.py
```

浏览器打开后，就可以直接开始旅行模拟。

## 测试

项目现在补了一组最基础的数据完整性测试，不依赖额外测试框架，可以直接运行：

```bash
python -m unittest discover -s tests
```

## GitHub 展示建议

如果你准备把这个仓库公开，建议再补 3 张图到 README：

- 首页创建角色页
- 游戏进行中的主界面
- 旅行结算页

比较推荐的做法是把图片放到 `docs/screenshots/`，再在 README 顶部加展示图。这样后面换图时不会改动太多正文结构。

## 玩法说明

你需要在有限天数内完成一段旅行。项目当前的核心资源和规则包括：

- `预算`：活动、住宿、移动都会花钱
- `体力`：景点、夜生活、跨城移动都会消耗体力
- `时间`：不同活动占用不同小时数
- `天气`：雨天会增加行动体力消耗
- `夜间交通限制`：夜里只允许纯航班类移动
- `住宿选择`：每天到 `08:00` 后需要先安顿住宿

如果钱花光、天数结束，或者选择主动结束行程，都会进入结算页。

## 为什么这个项目值得继续做

这个原型已经具备了一个小游戏最重要的东西：不是“功能拼盘”，而是已经有了一个完整循环。

用户进入项目后会经历：

1. 设定起点和预算
2. 开始旅行
3. 在城市里做选择
4. 因为资源约束被迫取舍
5. 获得结算结果

这意味着它已经不是单纯的 AI 展示页，而是一个可以继续产品化的雏形。

## 下一步最值得做的优化

### P0：先补稳定性

- 把 UI 和游戏逻辑进一步解耦，减少 `Streamlit session_state` 与业务逻辑强耦合
- 给核心流程补最小测试：`start_game / do_activity / travel_to / sleep / finish_game`
- 增加异常兜底和日志，避免 AI 接口失败时影响页面主流程
- 为依赖加版本号，避免未来环境漂移

### P1：增强可玩性

- 增加事件系统，例如被骗、捡漏、偶遇、限时活动
- 增加人物状态，例如心情、签证压力、旅行评分
- 为不同城市加入更明显的城市个性和稀有事件
- 加入成就系统和多结局设计，提升重复游玩价值

### P2：提升 GitHub 展示效果

- 补首页截图 / GIF
- 增加英文简介，方便公开展示
- 增加 `LICENSE`
- 初始化 git 仓库并整理首个公开版本提交

## 适合扩展的方向

- 做成更完整的 Thailand backpacker roguelike
- 加入 LLM 生成旅行事件和 NPC 对话
- 加入排行榜、种子挑战、固定剧情线
- 从 Streamlit 迁移到更适合游戏体验的前端框架

## 已知现状

- 当前更像“高完成度原型”而不是工程化产品
- 代码里仍有一些原型式写法，适合继续整理结构
- AI 图片与天气依赖外部接口，体验会受网络和额度影响

## License

本项目当前使用 `MIT License`，详见 [LICENSE](./LICENSE)。
