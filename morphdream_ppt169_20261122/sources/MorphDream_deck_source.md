# 梦蝶：为看见而物化 —— 汇报 PPT 主材料

> 本文件是 ppt-master 的主材料，按页给出标题、核心信息、页面内容、配图建议和讲者备注。
> **重要：本项目尚未开始实验。文中所有"结果"均为计划或预期，制作时不得改写成已获得的结论。**

---

## 项目基本信息

| 项目 | 内容 |
| --- | --- |
| 中文名 | 梦蝶：为看见而物化 |
| 英文名 | Protean Perception |
| 方法名 | MorphAction（梦蝶闭环） |
| 副标题 | 可重构机器人的跨形态主动视觉搜索 |
| 目标会议 | ICML 2027（摘要 2027 年 1 月 14 日，全文 1 月 22 日） |
| 一句话 | 机器人能看到什么取决于它的身体；因此"选择身体"本身就是一个感知决策 |
| 汇报人与单位 | （留空，由汇报人填写） |

## 全片叙事线

问题（身体决定能看到什么）→ 为什么现在做（多项实证表明瓶颈常在身体）→ 挑战 → 现有工作缺什么 → 核心思想（形态是视点代价地形，重构是信息采集动作）→ 方法（梦蝶闭环）→ 如何验证（实验与基线）→ 计划与风险 → 贡献。

---

## 第 1 页｜封面

- **标题**：梦蝶：为看见而物化
- **副标题**：可重构机器人的跨形态主动视觉搜索（Protean Perception）
- **其他信息**：方法名 MorphAction · 目标会议 ICML 2027 · 2026 年 11 月 · 汇报人与单位留空
- **配图建议**：★ 题图的简化版：一个米色的模块化机器人站在床边，床底有一个红色苹果，角落放一个小蝴蝶图标。
- **讲者备注**：今天汇报的问题可以用一句话概括：机器人能看到什么，取决于它的身体。所以，"选择用什么身体去看"本身就是一个感知决策。

## 第 2 页｜同一个目标，换一具身体才看得见

- **核心信息**：用一个例子讲清楚整个项目。
- **页面内容**：三格连环图，从左到右。
  1. **清醒：看不到**。四足形态站在床边，相机视线被床沿挡住，床底的苹果看不到。
  2. **梦：跨形态想象**。机器人在想象中试用三种形态：蛇形贴地看床底，能看到；人马形从上方看，看不到；潜望形态，部分可见。
  3. **变形并验证**。机器人变成蛇形钻到床底，真实的相机视线照到苹果。
  - 页面底部一句话：想象只用于决定下一步做什么，绝不当作证据写进记忆。
- **配图建议**：★ 图 1（附录 A）。
- **讲者备注**：这个例子包含了项目的全部要素：先判断为什么看不到，再在"梦"里试用不同的身体，只在值得时才真正变形，最后用真实观测验证。

## 第 3 页｜核心问题：机器人应当何时、以及如何改变身体来看？

- **核心信息**：问题拆成三个子问题，并有一个核心主张。
- **页面内容**：
  - 三个子问题：
    1. 用哪种形态去感知？
    2. 每种形态怎么感知？
    3. 何时变形、怎么变过去？
  - 核心主张（高亮框）：重构身体是一种信息采集动作。它抬高的是"能获得哪些证据"的上限，这是更多的思考、更好的视点规划都替代不了的。
  - 四个科学主张：
    - C1 存在性：变形确实扩展了可见集合。
    - C2 归因：能区分"位姿受限"和"身体受限"两类瓶颈。
    - C3 决策：知道何时变、变成什么，以及何时不该变。
    - C4 物理有效性：变形的代价与稳定性来自实测。
- **配图建议**：左侧三个子问题配简单图标；右侧主张高亮框；底部 C1–C4 四个小标签。
- **讲者备注**：注意 C3 里的"何时不该变"。变形有代价，一个好的系统应当经常选择不变形。

## 第 4 页｜证据表明：瓶颈常常在身体，而不在模型

- **核心信息**：近两年的多项研究从不同角度发现，"需要移动或改变身体"才是难点。
- **页面内容**（四张卡片）：
  1. **TVRBench**（2026 预印本）：只需原地转头时尚可，一旦需要移动身体，成功率大幅下降；最好的闭源模型成功率只有 12%。
  2. **PhysVLM-AVR**（NeurIPS 2025）与 **Theory of Space**（ICLR 2026）：模型能察觉信息缺失，却难以主动获取；让模型自己探索，反而比直接给它观测表现更差。
  3. **VLN-PE**（ICCV 2025）：同一导航模型在人形、四足、轮式机器人上性能明显下降，原因之一是受限的观测空间。
  4. **相机高度研究**（2020）：较高的相机整体视野更好，但目标藏在地面柜子里时，低相机反而更有利。
- **配图建议**：四张等大的卡片，每张一个图标和一行结论。
- **讲者备注**：这些工作都没有让机器人改变身体，但它们共同指向一个现象：观测空间由身体决定，而现有模型很难跨越这一限制。

## 第 5 页｜难点不在"换身体"本身，而在何时换、换成什么、值不值得

- **核心信息**：六个挑战。
- **页面内容**（六宫格）：
  1. **代价地形随身体改变**：可达性、成像质量和代价同时变化。
  2. **回报取决于信念且边际递减**：看过的地方不再提供新信息。
  3. **能力耦合**：变形后某些动作不可达，移动能力也随之改变，记作 $P(m) \subseteq P$。
  4. **变形有真实代价**：耗时、跌倒、过渡失败；系统必须学会"不变形"。
  5. **每种形态的感知运动协调不同**：稳像、步态相位、自遮挡。
  6. **新形态要即插即用**：不能每增加一种形态就重新训练。
- **配图建议**：2×3 六宫格，每格一个图标、一个短标题、一行说明。
- **讲者备注**：其中第 3、4 条，加上"会选择不变形"，是本项目与现有工作区分的三道护城河。

## 第 6 页｜现有工作至少缺少其中两点

- **核心信息**：按六个维度对比，没有一类工作同时满足。
- **页面内容**（表格，"本项目"一行高亮）：

| 工作类别 | 传感器位姿可动 | 身体构型在线改变 | 改变是为了感知 | 建模能力耦合 | 实测变形代价 | 会选择"不变形" |
| --- | :-: | :-: | :-: | :-: | :-: | :-: |
| 主动视觉 / 具身问答 | ✓ | ✗ | — | ✗ | ✗ | ✗ |
| 视点 / 变焦基准 | ✓ | ✗ | — | ✗ | ✗ | ✗ |
| 变形机器人（为运动） | ✗ | ✓ | ✗ | 部分 | 部分 | ✗ |
| 在线变形强化学习 | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| 感知驱动重构（Daudelin 2018） | ✓ | ✓ | ✗（为执行） | ✗ | ✗ | ✗ |
| 姿态服务感知（POSE） | ✓ | 仅姿态 | ✓ | ✗ | ✗ | ✗ |
| 设计期可见—可达（VRW） | — | 设计期 | ✓ | ✓ | ✗ | — |
| 跨具身基础模型 | — | 视为干扰 | ✗ | ✗ | ✗ | ✗ |
| **本项目** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

- **配图建议**：可编辑表格；✓ 用强调色，✗ 用浅灰。
- **讲者备注**：跨具身基础模型（RING、NavFoM、X-VLA 等）把身体差异当作要"泛化掉"的干扰，正好是我们的反面：我们把身体差异当作可利用的感知资源。

## 第 7 页｜与最接近工作的区别

- **核心信息**：逐一说明最接近的六类工作和我们的区别。
- **页面内容**（三列表格）：

| 工作 | 它做了什么 | 我们的区别 |
| --- | --- | --- |
| Daudelin 等，Science Robotics 2018 | 模块化机器人先感知环境，再选构型去执行任务 | 方向相反：我们为获取证据而变形，并计入机动性代价 |
| Learning to Reconfigure，ICML 2026 | 关节锁定定义构型，调度器为跨越地形而切换，只看本体状态 | 切换的理由是视觉证据，由感知瓶颈触发 |
| POSE，2026 预印本 | 腿足机器人调整俯仰、横滚，扩大感知覆盖 | 姿态不改变能力集合；我们改变接触模式和可达动作 |
| VRW，2026 预印本 | 提出设计期的"可见—可达工作空间"指标 | 我们是任务进行中的在线选择 |
| EMOS，ICLR 2025 | 大模型读取"机器人简历"，在多台机器人间分配任务 | 我们在一台机器人的多个形态间选择，并计入变形代价 |
| Pathak 等 NeurIPS 2019；DittoGym ICLR 2024 | 任务中在线改变形态 | 它们的目标是运动，我们的目标是感知证据 |

- **配图建议**：可编辑表格；第一列加粗。
- **讲者备注**：审稿人最可能问的是"Daudelin 已经做过感知驱动重构"和"POSE 也用身体姿态做感知"，这一页正面回答。

## 第 8 页｜一种形态就是一张"视点代价地形"，重构就是在地形之间跳转

- **核心信息**：项目的核心思想与庄周梦蝶的隐喻。
- **页面内容**：
  - 视觉是在对光场采样；身体决定每个视点的三件事：能否到达、成像质量、代价。
  - 真正离散的重构有三类：接触模式切换、刚度或锁定切换、拓扑或传感器布置切换。本项目做前两类。
  - 庄周梦蝶的三个关键词：
    - **物化**：形态之间可以转化。
    - **梦**：变形之前，先在想象中以另一具身体的视角看一眼。
    - **梦醒之分**：想象不等于证据。
- **配图建议**：左边是同一房间里两种形态的"可见区域"示意（四足看到台面，蛇形看到床底）；右边放蝴蝶图标和三个关键词。
- **讲者备注**：《庄子·齐物论》："昔者庄周梦为胡蝶，栩栩然胡蝶也……此之谓物化。"庄周在梦里不是旁观蝴蝶，而是以蝴蝶的身体去感知，这正是跨形态想象要做的事。

## 第 9 页｜问题定义：三层动作，以最短时间获得足够证据

- **核心信息**：形式化定义，以及哪些可以简化、哪些不能。
- **页面内容**：
  - 任务：给定语言描述的目标（如"找到苹果"），在未知室内场景中搜索，直到获得满足要求的视觉证据。
  - 信念：占据地图、语义地图、目标位置后验 $p_t(h)$。
  - 三层动作：视点层（移动、转向、注视）；注意力层（裁剪、放大、回看）；形态层（切换形态，代价来自履历）。
  - 目标函数：$\min_{\pi}\ \mathbb{E}\big[\,T_{\text{evidence}} + T_{\text{think}} + \lambda_F\,\mathbb{1}[\text{fall}]\,\big]$
  - 简化原则（两栏）：
    - 必须保留：形态之间互补；需要看哪里取决于已经看到了什么；过渡有真实代价；存在强基线；想象只能使用机器人自己的记忆。
    - 可以简化：固定拓扑不做对接；形态模板由人给定；经典步态加感知调制；静态场景、单目标；观测用深度加语义。
- **配图建议**：左侧三层动作做成阶梯图；右侧两栏对比。
- **讲者备注**：简化的原则借鉴 Learning to Reconfigure：问题形式化可以大胆简化，但不能简化掉让问题成立的那部分。思考时间也计入目标，这样"想太久"同样会被惩罚。

## 第 10 页｜梦蝶闭环：每一步都"提议—想象—择优"

- **核心信息**：方法总览。
- **页面内容**：
  - 五个模块依次运行：(a) 证据需求解析 → (b) 感知瓶颈诊断 → (c) 动作提议 → (d) 跨形态想象评估 → (e) 执行与验证，然后回到 (a)。
  - 三类记忆：场景记忆（占据、语义、目标假设）、情景记忆（动作、观测、失败案例）、形态履历。
  - 底层：L1 身体层，即步态（CPG）加感知调制（注视、速度、停顿、姿态）。
  - 梦醒分离：(d) 想象出的观测不写入记忆；只有 (e) 验证过的真实证据才能更新场景记忆。
- **配图建议**：★ 图 2（附录 A），做成可编辑流程图；(d) 用强调色；(d) 到记忆之间画一条带叉号的虚线。
- **讲者备注**：整个框架不需要符号规划器，是一个每步重新决策的闭环。

## 第 11 页｜一具模块化"超集机器人"，五种形态

- **核心信息**：实验平台与候选形态。
- **页面内容**：
  - 装配体：4 节脊柱模块（节间有偏航和俯仰两个自由度）、3 对各 3 自由度的腿、带深度相机和颈部的头部模块。拓扑固定，不做对接。
  - 形态 = 锁定哪些关节 + 锁定角度 + 哪些肢体着地。
  - 五种形态（表格）：

| 形态 | 视觉生态位 | 感知运动协调的难点 |
| --- | --- | --- |
| 六足 | 中等高度，最稳，可以边走边看 | 利用稳定性连续扫视；前腿自遮挡 |
| 四足 | 中等高度，转场最快 | 小跑抖动大，需要"跑过去、停下看" |
| 人马形 | 视点高，上身可独立转动注视 | 下身行走时保持上身稳定 |
| 蛇形 | 最低、最窄，能进床底和沙发下 | 头部随身体摆动，需要主动稳像 |
| 潜望 | 身体留在窄处，头部抬起局部扫视 | 抬头时支撑面小，有倾覆风险 |

  - 形态筛选：先提出候选，再实测履历，最后选出能覆盖全部藏匿类型、冗余最小的子集。直立双足作为可选项。
- **配图建议**：★ 图 3 的上半部分：同一机器人的五种形态并排，标出相机高度和锁定关节。
- **讲者备注**：表中相机高度等数值都要由仿真实测给出，这里只是定性描述。

## 第 12 页｜高层只通过"履历"认识身体，所以新形态可以即插即用

- **核心信息**：形态履历与能力耦合。
- **页面内容**：
  - 履历字段：可达相机位姿、通过尺寸、各步态速度、成像稳定性、注视自由度、自遮挡、过渡耗时与成功率、能耗与风险。全部由物理仿真实测，不手填。
  - 能力耦合 $P(m) \subseteq P$：变形扩展了一些视点，同时收缩了另一些动作。
  - 借鉴：EMOS 的"机器人简历"；PhysVLM 把可达空间投影成图像遮罩输入视觉语言模型。我们为每种形态生成"可见—可达遮罩"，交给提议器。
- **配图建议**：★ 图 3 的下半部分：五个雷达图，轴为相机高度、通过间隙、速度、稳定性、注视自由度、过渡代价。
- **讲者备注**：因为高层只认履历，给出新形态的履历，系统就能直接使用它，这是零样本实验 E2 的基础。

## 第 13 页｜先问"为什么看不到"，再决定"要不要换身体"

- **核心信息**：感知瓶颈诊断。
- **页面内容**（表格）：

| 可见性条件 | 不满足时的瓶颈 | 首选补救 |
| --- | --- | --- |
| 视线无遮挡 | 遮挡 | 视点层；补救视点不可达时转形态层 |
| 目标在视场内 | 视场 | 视点层：转向、调整注视 |
| 分辨率足够 | 尺度 | 注意力层：裁剪放大；或走近 |
| 视角合适 | 视角 | 视点层：换个角度 |
| 成像质量够好 | 模糊或抖动 | 停顿、稳像 |
| **补救视点可达** | **可达性** | **形态层：换成能到达的形态** |

  - 触发形态层的条件：补救视点不在当前形态的可达集内，或者在另一种形态下代价低得多。
  - 这一步对应 C2：区分"位姿受限"和"身体受限"。
- **配图建议**：右侧示意图：站姿的视线被床沿挡住；补救视点在离地约 10 厘米处，只有蛇形能到达。
- **讲者备注**：这个触发条件可以在场景记忆上直接计算，比"普通主动感知不够时再变形"更有原则。

## 第 14 页｜在记忆里"做梦"：变形之前先估计能看到多少

- **核心信息**：跨形态想象评估器。
- **页面内容**：
  - 证据增益：$\text{Gain}(m, v) \approx \sum_{h} p_t(h)\cdot P(\text{可见且可识别} \mid v, m, h) - \lambda \cdot \text{Cost}(m, v)$
  - 三层想象，按需升级：
    - 第 0 层：在场景记忆中从候选相机位姿做光线投射，毫秒级，每个候选都算。
    - 第 1 层：根据家具类别和可见下沿，估计未知区域的离地间隙和内部空间。
    - 第 2 层（可选）：用生成式世界模型补出画面，只在决策胶着且涉及变形时使用。
  - 保守打分：依赖未知空间的部分取置信下界。
  - 评估器不需要训练；对新形态的零样本能力来自公式结构本身。
- **配图建议**：上方公式；中间三层阶梯；下方"想象 ✗ 记忆"的示意。
- **讲者备注**：未知区域里，影响决策的往往不是"长什么样"，而是"空间多大、哪具身体能进去"，所以第 1 层不需要生成像素。

## 第 15 页｜贪心就够了吗？自适应次模性给出依据，切换代价留出研究空间

- **核心信息**：决策方式与测试时计算。
- **页面内容**：
  - 提议：结构化思维链，一次给出 4 到 8 个候选。
  - 选择：每步重新决策的贪心；只有候选中出现形态切换时，才做两步前瞻。
  - 理论依据：问题满足自适应次模性时，自适应贪心接近最优（Golovin & Krause, JAIR 2011）；切换代价会破坏这一保证，这是后续理论工作的切入点。
  - 自适应计算分配：前几名候选越接近、切换代价越大，就想得越多，即"变形之前多想想"。
  - 关键科学问题：思考能否替代身体？
- **配图建议**：左边是"提议 → 想象 → 择优"的循环小图；右边是计算预算随候选差距变化的示意刻度。
- **讲者备注**：缩小目标位置假设本身就是自适应次模问题的典型例子，所以贪心闭环不是凑合，而是有理论根据的选择。

## 第 16 页｜大模型负责提议与语义，几何与数值交给模型验证

- **核心信息**：开源大模型在框架中的分工。
- **页面内容**（表格）：

| 模块 | 实现 |
| --- | --- |
| 证据需求解析 | 开源大语言模型 |
| 瓶颈诊断 | 视觉语言模型提供语义线索，几何计算判断可见性和可达性 |
| 动作提议 | 视觉语言模型做结构化思维链，输入记忆摘要和各形态的"可见—可达遮罩" |
| 证据增益评估 | 几何想象、结构先验和履历，不用大模型 |
| 执行验证 | 开发时用仿真真值加噪声，最终评估用开放词汇检测器或视觉语言模型 |
| 情景记忆（可选） | 借鉴 Reflexion，把失败反馈写成文字经验 |

  - 原则：大模型不进入控制回路，也不独自做最终决策。
  - 依据：大模型单独做规划效果不好，"大模型提议、模型验证"的闭环更有效（LLM-Modulo 系统研究，2025）。
- **配图建议**：可编辑表格，"不用大模型"的一行用强调色标出。
- **讲者备注**：我们也考虑过用进化式程序搜索来改进评估器，但它会让评估器拟合训练场景，削弱泛化，所以放弃。

## 第 17 页｜仿真平台：MuJoCo Warp 加 MolmoSpaces，五类藏匿位置

- **核心信息**：实验环境。
- **页面内容**：
  - 仿真：MuJoCo Warp 在 A100 上批量仿真，并用 GPU 批量渲染深度和分割图。Isaac Sim 的渲染不支持 A100 这类没有 RT 核心的 GPU，因此不选。
  - 场景：MolmoSpaces，包含 23 万多个室内场景和 13 万多个带元数据的物体；按场景来源留出测试集。
  - 五类藏匿位置：低矮缝隙（床底、沙发底）、高处（柜顶、台面深处）、遮挡物之后、柜内低层开放格、远处的小目标。
  - 观测：深度图加语义掩码（仿真真值叠加噪声），RGB 可选。
  - 数据划分：开发集、验证集、测试集；另外留出一种形态，专门用于零样本实验。
- **配图建议**：五类藏匿位置各一张小示意图，排成一行。
- **讲者备注**：每类藏匿位置都应有一种形态是唯一高效的观察方式，这样才能检验"换身体"的价值。

## 第 18 页｜从"不能变"到"自由相机"，基线覆盖所有替代解释

- **核心信息**：基线设计。
- **页面内容**（表格）：

| 基线 | 回答的质疑 |
| --- | --- |
| 最佳固定形态 | 重构是否必要 |
| 固定形态加连续姿态与注视调节（强基线） | 姿态调节是否就够了 |
| 固定升级规则：视点 → 注意力 → 形态 | 由证据增益决定何时变形是否更好 |
| 纯思维链智能体 | 几何想象是否必要 |
| VLFM 式语义前沿探索 | 与现有语义搜索方法相比如何 |
| 只想象、不变形 | 想象能否替代真实变形 |
| 自由相机（上界） | 这是否只是"换了个更高的相机" |
| 理想形态选择（上界） | 离最优还有多远 |
| 训练版评估器 | 免训练能否追平训练 |

- **配图建议**：可编辑表格；两个"上界"行用浅色底标出。
- **讲者备注**：自由相机上界不受身体约束，用来说明真实身体约束下的取舍才是问题本身。

## 第 19 页｜五组实验对应四个科学主张

- **核心信息**：实验安排，以及预期的核心结果图。
- **页面内容**：

| 实验 | 内容 | 对应主张 |
| --- | --- | --- |
| E1 主对比 | 全部藏匿类型上与所有基线比较 | C1、C3 |
| E2 零样本新形态 | 开发全程留出一种形态，测试时只提供履历 | C3 |
| E3 思考与身体的扩展曲线 | 改变候选数、前瞻深度和形态库规模 | C1 |
| E4 切换何时值得 | 按藏匿类型、距离和切换代价分组，统计"不变形"的比例 | C3 |
| E5 消融 | 去掉瓶颈诊断、结构先验、两步前瞻；违反梦醒分离 | C2、C3 |
| 诊断准确率 | 判断"位姿受限"还是"身体受限"的准确率 | C2 |
| 物理有效性 | 履历实测、跌倒率、过渡成功率 | C4 |

  - 指标：成功率、获得证据的用时（含思考时间）、切换次数、跌倒率、过渡失败率；至少 8 个随机种子，报告中位数和四分位距。
- **配图建议**：★ 图 4（附录 A）："思考替代不了身体"的预期曲线。**图上必须标注"预期结果（示意）"。**
- **讲者备注**：我们预期固定身体的曲线会很快到顶：物理上到不了的视点，想得再多也看不到；增加形态则会抬高上限。

## 第 20 页｜9 周冲刺 ICML 2027：1 月 3 日的 G3 决定去留

- **核心信息**：实施计划与人机协作方式。
- **页面内容**：
  - 时间线（2026 年 11 月 23 日至 2027 年 1 月 22 日）：
    - S0 基础设施与可行性验证：11/23–11/29
    - S1 超集机器人与身体层：11/23–12/6
    - S2 履历与形态库：12/7–12/13
    - S3 场景记忆与感知：11/30–12/13
    - S4 瓶颈诊断与评估器：12/7–12/20
    - S5 提议器与决策闭环：12/21–1/3
    - S6 基线：12/21–1/3
    - S7 实验与分析：12/28–1/17
    - S8 论文支撑：1/4–1/22
  - 关口：G1 12 月 6 日（三种形态跑通）；G2 12 月 20 日（评估器达标）；G3 1 月 3 日（E1 初版超过强基线，决定是否冲刺）；G4 1 月 14 日（注册摘要）；1 月 22 日提交全文。
  - 分工：人做判断题，编码智能体（Codex 等）做实现题；Mac 负责开发调试，A100 负责批量仿真、渲染和模型服务。
- **配图建议**：可编辑甘特图，九行任务条；G3 用强调色实线，其余关口用虚线。
- **讲者备注**：如果 G3 没有通过，就转投截稿更晚的会议，并利用多出的时间补齐形态。

## 第 21 页｜主要风险都有明确的对策

- **页面内容**（表格）：

| 风险 | 对策 |
| --- | --- |
| 距截稿只有约 9 周 | 先用三种形态跑通全流程，再补齐其余形态 |
| 多形态底层实现量大 | 经典步态加感知调制，不做端到端运动学习 |
| 想象在未知区域不准 | 结构先验加保守打分；生成式想象只用于复核 |
| 收益被连续姿态调节抵消 | 设为强基线；若收益有限，结论转为刻画"何时重构值得" |
| 提示词和参数过拟合开发场景 | 严格的数据划分，提前冻结提示词 |
| 大模型推理延迟 | 低频调用、缓存，并把思考时间计入任务耗时 |

- **配图建议**：可编辑表格。
- **讲者备注**：第四条最关键：即使收益不如预期，"何时重构值得"本身也是有价值的结论。

## 第 22 页｜预期贡献：为看见而改变自己

- **页面内容**：
  1. **新问题**：把形态切换建模为信息采集动作。
  2. **新方法**：瓶颈与履历的分解，加上跨形态想象和梦醒分离；评估器免训练，能零样本使用新形态。
  3. **新基准**：多形态主动视觉搜索任务套件与评测协议。
  4. **实证结论**：思考替代不了身体；并给出"何时不该变形"的条件。
  - 收尾一句："此之谓物化"——为看见而改变自己。
- **配图建议**：回到封面的蝴蝶意象，与第 1 页首尾呼应。
- **讲者备注**：谢谢大家，欢迎提问。

---

## 备份 B1｜与 AI 编码智能体协作的方式

- 人负责判断题（形态模板、阈值、降级、冻结提示词、解读结果），编码智能体负责实现题（代码、测试、实验、报告）。
- 防泄漏规则都写成代码和测试：
  - 想象模块不能读取仿真器状态；
  - 想象出的观测不能写入场景记忆；
  - 提示词冻结后带哈希；测试集评测需要人工打开开关。
- 仓库根目录和想象模块目录各有一份 AGENTS.md；每个任务用统一模板的任务卡；每周五做一次集成测试。

## 备份 B2｜主要参考文献

1. Bajcsy, Aloimonos, Tsotsos. Revisiting active perception. Autonomous Robots, 2018.
2. Daudelin 等. An integrated system for perception-driven autonomy with modular robots. Science Robotics, 2018.
3. Learning to Reconfigure: Co-designing reconfigurable robots for heterogeneous locomotion. ICML 2026.
4. Pathak 等. Learning to control self-assembling morphologies. NeurIPS 2019.
5. Huang 等. DittoGym: Learning to control soft shape-shifting robots. ICLR 2024.
6. Chen 等. EMOS: Embodiment-aware heterogeneous multi-robot operating system with LLM agents. ICLR 2025.
7. Zhou 等. PhysVLM: Enabling visual language models to understand robotic physical reachability. CVPR 2025.
8. PhysVLM-AVR. NeurIPS 2025.
9. Theory of Space. ICLR 2026.
10. VLN-PE: Rethinking the embodied gap in vision-and-language navigation. ICCV 2025.
11. TVRBench（Where to Look）. arXiv:2606.01247, 2026.
12. POSE: Pose-aware legged robot semantic exploration with omnidirectional perception in confined unknown environments. arXiv:2609.19460, 2026.
13. Visible-reachable workspace for perception-aware humanoid design（VRW）. arXiv:2609.08905, 2026.
14. Yokoyama 等. VLFM: Vision-language frontier maps for zero-shot semantic navigation. ICRA 2024.
15. Yang 等. MindJourney: Test-time scaling with world models for spatial reasoning. NeurIPS 2025.
16. Lu 等. GenEx（Generative World Explorer）. ICLR 2025.
17. Golovin, Krause. Adaptive submodularity. JAIR, 2011.
18. Kaelbling, Lozano-Pérez. Integrated task and motion planning in belief space. IJRR, 2013.
19. Mendez-Mendez. A systematic study of large language models for task and motion planning with PDDLStream. 2025.
20. Shinn 等. Reflexion: Language agents with verbal reinforcement learning. NeurIPS 2023.
21. MolmoSpaces. arXiv:2602.11337, 2026.
22. MuJoCo Warp（Google DeepMind 与 NVIDIA）.

---

## 附录 A｜★ 配图的英文生图 prompt

### 图 1 题图：在另一具身体里做梦（用于第 1、2 页）

A clean, flat vector illustration for a machine learning paper teaser figure, white background, landscape 16:9, three panels from left to right connected by arrows.
Panel 1, caption "Awake: target hidden": a cozy living-room cross-section; a modular segmented robot in quadruped form (warm beige rounded modules, a small depth camera on its head) stands next to a bed; a red apple lies hidden under the bed; a semi-transparent gray camera frustum from the robot's head is blocked by the bed frame.
Panel 2, caption "Dream: cross-morphology imagination": the same robot with a soft blue thought bubble containing three small imagined views: (a) snake form lying flat and looking under the bed, apple visible, green check mark; (b) centaur form looking from above, apple not visible, red cross; (c) periscope form, apple partially visible. A tiny butterfly icon sits in the corner of the bubble.
Panel 3, caption "Transform and verify": the robot reconfigured into snake form crawls under the bed; its real camera frustum reaches the apple, highlighted in green.
Small footer text: "Imagined views guide actions but are never written into memory".
Style: minimal, consistent line weight, muted palette (beige robot, gray furniture, red apple, blue dream bubble), no photorealism, sans-serif font, no text other than the captions given.

### 图 2 方法总览：梦蝶闭环（用于第 10 页）

A clean academic system diagram, white background, landscape 16:9, flat vector style, rounded rectangles with thin dark-gray outlines, one blue accent color for the imagination module.
Left: an "Environment" box with a small illustration of a cluttered room and a modular robot; below it a box "Task: Find the apple".
Center column titled "Agent loop", five stacked boxes connected by downward arrows: "(a) Evidence Requirement Parser"; "(b) Perceptual Bottleneck Diagnoser: occlusion / FoV / scale / viewing angle / image quality / reachability"; "(c) Action Proposer (structured CoT, N candidates): view-level / attention-level / morphology-level"; "(d) Cross-Morphology Imagination Evaluator: Tier 0 geometric ray casting, Tier 1 structural priors, Tier 2 generative (optional)"; "(e) Execute & Verify".
Box (d) is highlighted in blue with a small butterfly icon. A loop arrow from (e) back to (a) is labeled "re-plan every step".
Right column titled "Memory", three boxes: "Scene Memory: occupancy, semantics, unseen regions, target hypotheses"; "Episodic Memory: actions, observations, failures"; "Morphology Resume: reachable camera poses, clearance, speed, jitter, transitions (time, success)".
Solid arrows from the memory boxes to (b), (c) and (d) labeled "retrieve"; a solid arrow from (e) to Scene Memory labeled "verified evidence only"; a dashed red arrow from (d) toward Scene Memory crossed by a red X, labeled "imagined views never written".
Bottom strip spanning the full width: "L1 body layer: gait (CPG) + perceptual modulation (gaze, speed, pause, posture)", connected to (e).
Sans-serif typography, labels exactly as given, no extra text.

### 图 3 一具身体，多种视点（用于第 11、12 页）

A clean academic figure, white background, landscape. Title: "One body, many viewpoints".
Top row: the same modular robot (identical warm beige rounded modules, a head module with a small camera) shown in five configurations side by side on a shared ground line: "Hexapod", "Quadruped", "Centaur", "Snake", "Periscope". For each, draw the camera as a small blue dot with a light-blue view cone, and a dashed horizontal line marking camera height. Locked joints are marked with small padlock icons; ground-contact feet are marked with small dark dots.
Bottom row: five small radar charts, one under each form, with six axes: "Camera height", "Clearance", "Speed", "Stability", "Gaze freedom", "Transition cost". Each radar shape is different; all use the same color scheme.
Flat vector style, consistent proportions, no photorealism, sans-serif labels.

### 图 4 预期核心结果：思考替代不了身体（用于第 19 页，必须标注为示意）

A clean line chart for a machine learning paper, white background.
X axis: "Test-time compute budget (candidates x lookahead depth)", log scale. Y axis: "Search success within time limit".
Three curves: "Fixed body" in gray rises and then plateaus low; "Fixed body + posture control" in light blue plateaus slightly higher; "Reconfigurable (ours)" in dark blue rises to a much higher plateau.
Thin dashed horizontal lines mark each plateau; an annotation arrow between the lowest and highest plateau is labeled "Thinking cannot replace a body".
A clear label in the top-right corner: "Expected result (schematic)".
Minimal style, light horizontal gridlines only, sans-serif labels, legend in the top-left corner.

---

## 附录 B｜关键事实速查（制作时以此为准）

| 事实 | 内容 |
| --- | --- |
| ICML 2027 截止日期 | 摘要 2027 年 1 月 14 日；全文 2027 年 1 月 22 日 |
| 计划周期 | 2026 年 11 月 23 日至 2027 年 1 月 22 日，共 9 周 |
| 关口 | G1 12/6，G2 12/20，G3 1/3，G4 1/14 |
| 形态 | 六足、四足、人马形、蛇形、潜望；直立双足可选 |
| 想象层级 | 第 0 层几何光线投射；第 1 层结构先验；第 2 层生成式（可选） |
| 提议候选数 | 每步 4 到 8 个 |
| 随机种子 | 每个结论至少 8 个 |
| 仿真与渲染 | MuJoCo Warp，A100；Mac 用于开发调试 |
| 场景来源 | MolmoSpaces：23 万多个室内场景，13 万多个物体 |
| 实验结果 | 尚未开始，全部为计划或预期 |
