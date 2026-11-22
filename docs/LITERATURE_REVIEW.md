# 变形感知（Protean Perception）相关文献综述

> 项目核心命题：机器人的身体构型决定了它"能看到什么"；因此"选择身体"本身是一个感知决策，它要用证据收益去换时间、能量和机动性（能力耦合：P(m) ⊆ P）。
>
> 检索日期：2026-11-17。重点覆盖 Science / Nature 系列 / PNAS / Science Robotics 等期刊，以及 ICLR / NeurIPS / ICML / CVPR / ICCV / ECCV / CoRL / RSS 等会议；最后单列与本项目最接近的 2026 年预印本。
>
> 标记：★ = 与本项目最接近、写相关工作时必须正面区分；[n] 对应文末参考文献编号。发表信息的核实情况见文末"核实说明"。

---

## 0. 一页结论

1. **主动感知有四十年的理论积累，但"动作"几乎总是指移动相机或移动身体，从未指改变身体本身。** 从 Bajcsy [1]、Aloimonos [2] 到具身问答 [58–62]，再到最新的视点/变焦基准 [66, 67]，感知动作空间都是"同一个身体的位姿"。
2. **变形机器人在 Nature / Science 系期刊上很热，但变形的目的几乎都是运动（跨地形、跨介质）。** Baines 等 [16]、M4 [17]、可重构模块腿 [19]、Learning to Reconfigure [21] 都为移动而变形；只有 Daudelin 等 [15] 让感知"驱动"重构，但方向是"先看清环境，再变形去干活"，而不是"为了看清而变形"。
3. **ICLR / NeurIPS 的形态协同设计主线（NGE → Transform2Act → BodyGen、DittoGym 等）优化的是离线设计或运动奖励，**不讨论"在一次任务中，此刻是否值得变形去获取证据"。
4. **跨具身基础模型（RING、NavFoM、X-VLA、CanonNav 等）把身体差异当作要"泛化掉"的干扰，**正好是本项目的反面：我们把身体差异当作可利用的感知资源。
5. **两条 2026 年预印本最接近：** POSE [68] 让腿足机器人调整身体位姿来扩大感知覆盖，但身体和能力不变；VRW [69] 把"可见—可达"作为人形机器人传感器布置的设计期指标，但不做在线选择。
6. **研究空白（本项目的定位）：** 目前没有工作把"在线改变身体构型"当作感知动作，同时 (a) 建模变形对机动性的约束（能力耦合），(b) 使用实测的变形代价，(c) 会判断何时**不**该变形。这三点分别对应计划中的 C1–C4 主张。

---

## 1. 主动感知的理论根基

| 文献 | 发表 | 核心内容 | 对本项目的意义 |
|---|---|---|---|
| Bajcsy, *Active perception* [1] | Proc. IEEE 1988 | 提出感知是"有目的地控制传感器参数以获取信息"的过程 | 本项目问题定义的起点；我们把"传感器参数"推广到"身体构型" |
| Aloimonos 等, *Active vision* [2] | IJCV 1988 | 证明主动观察者能把若干病态视觉问题变为良态 | 支撑"换身体 = 换可解问题集合"的论证 |
| Bajcsy, Aloimonos, Tsotsos, *Revisiting active perception* [3] | Auton. Robots 2018 | 系统化主动感知的"为何、何时、如何、何处"框架 | 可直接借用其分类来组织我们的问题陈述 |
| O'Regan & Noë, 感觉运动理论 [4] | BBS 2001 | 视觉是对"感觉运动依存关系"的掌握，而非内部图像 | 哲学层面支撑：身体能做的动作决定能看到什么 |
| Gottlieb & Oudeyer [5] | Nat. Rev. Neurosci. 2018 | 主动采样与好奇心的神经科学框架：信息价值与代价的权衡 | 为"证据收益 vs. 时间/能量代价"的决策形式提供认知科学依据 |
| MacIver 等 [6] | PNAS 2017 | 脊椎动物登陆前眼睛已大幅增大、视距大增，感知范围改变了可行的行为规划 | 生物学先例：身体结构的改变先于并决定了"能看多远" |

---

## 2. 具身智能与形态计算

| 文献 | 发表 | 核心内容 | 对本项目的意义 |
|---|---|---|---|
| Pfeifer, Lungarella, Iida [7] | Science 2007 | 形态、材料与控制共同产生智能行为（形态计算） | 经典引用：身体不只是执行器，也塑造信息结构 |
| Gupta 等, DERL [8] | Nat. Commun. 2021 | 在复杂环境中同时演化形态并学习控制，形态影响学习速度与泛化 | 说明"形态—能力"耦合是可度量的 |
| Kriegman 等 [9] | PNAS 2020 | 计算机设计、细胞组装的可重构生物体（xenobots） | 可重构"身体"作为设计变量的极端例子 |
| Sims, *Evolving virtual creatures* [10] | SIGGRAPH 1994 | 形态与控制器联合演化的开山之作 | 协同设计的历史起点 |

---

## 3. 变形、可重构与模块化机器人

| 文献 | 发表 | 核心内容 | 对本项目的意义 |
|---|---|---|---|
| Yim 等 [11] | IEEE RAM 2007 | 模块化自重构机器人的挑战与展望 | 领域综述，用于定义"可重构" |
| Zykov 等 [12] | Nature 2005 | 模块机器人自我复制 | 模块化机器人进入顶刊的早期代表 |
| Rubenstein 等 [13] | Science 2014 | 千台机器人的可编程自组装 | 群体形态构建 |
| Li 等, 粒子机器人 [14] | Nature 2019 | 松耦合组件依靠统计力学实现整体运动 | 形态由大量单元涌现 |
| ★ Daudelin 等 [15] | Science Robotics 2018 | 模块化机器人先感知环境，再根据环境选择构型完成任务 | **最需要区分的早期工作**：它是"感知 → 选构型去执行"，我们是"选构型 → 为了感知"，并且考虑变形对机动性的代价 |
| ★ Baines 等 [16] | Nature 2022 | 通过自适应形态发生，让机器人在陆地/水中切换肢体形态 | 变形为了跨介质运动，不涉及感知 |
| ★ Sihite 等, M4 [17] | Nat. Commun. 2023 | 轮/腿/推进器"附肢再利用"，在多种运动模式间切换 | 同上：变形服务于运动；可作为"变形有代价"的实物证据 |
| 物质化机器人集群 [18] | Science 2025 | 机器人集群可时空调控整体强度与形状 | 形态可编程的最新顶刊进展 |
| ★ 可重构模块腿 [19] | PNAS 2025（arXiv 2505.00784） | 自主模块腿可拼成多种腿足"元机器"，敏捷运动且损伤后可重组 | 与本项目硬件形态最接近的顶刊工作；变形只为运动 |
| Shah 等 [20] | Adv. Mater. 2021 | 变形机器人的仿生、仿真与实现综述 | 引用以界定"shape-changing robots"术语 |
| ★ Learning to Reconfigure [21] | ICML 2026 | 固定骨架 + 关节锁定定义构型，协同设计构型库与调度器以跨越异质地形 | **本项目仿真基础设施的直接来源**；它的调度器是"盲"的（只看本体状态），我们把视觉证据作为重构的理由 |

---

## 4. 形态—控制协同设计（ICLR / NeurIPS 主线）

| 文献 | 发表 | 核心内容 | 对本项目的意义 |
|---|---|---|---|
| NGE [22] | ICLR 2019 | 用图网络演化机器人结构 | 早期 ICLR 协同设计 |
| ★ Pathak 等, 自组装形态 [23] | NeurIPS 2019 | 智能体在任务中动态连接/断开肢体，形成新形态 | **"在线改变形态"在 ML 顶会的先例**；目标是运动与泛化，不涉及感知 |
| Transform2Act [24] | ICLR 2022 | 把"变形"作为 MDP 中的一个阶段，先设计再控制 | 形态决策入 RL 的范式 |
| Evolution Gym [25] | NeurIPS 2021 | 软体机器人协同设计基准 | 基准设计参考 |
| SoftZoo [26] | ICLR 2023 | 多环境软体动物形态—控制基准 | 同上 |
| ★ DittoGym [27] | ICLR 2024 | 学习控制可在任务中改变形状的软体机器人 | 与 [23] 一样是"在线变形"，但仍以运动/操作为目标 |
| BodyGen [28] | ICLR 2025 | 高效形态协同设计，Learning to Reconfigure 的代码基础 | 代码与形态表示可复用 |
| RoboGrammar [29] | ACM TOG 2020 | 用图语法搜索地形最优的机器人结构 | 构型库生成的离散搜索参考 |
| Ha [30] | Artificial Life 2019 | 把身体参数与策略一起用 RL 优化 | 说明"身体参数可作为可学习变量"的简洁形式化 |

**小结：** 这一主线证明"形态是可优化变量"已被顶会接受，但目标函数几乎都是运动奖励。我们提出的"感知收益 − 变形代价"是一个新的目标，并且决策发生在任务进行中而非设计期。

---

## 5. 形态无关 / 跨形态控制

| 文献 | 发表 | 核心内容 | 对本项目的意义 |
|---|---|---|---|
| NerveNet [31] | ICLR 2018 | 用图网络表示策略，实现跨形态迁移 | 跨形态控制起点 |
| SMP [32] | ICML 2020 | 共享模块化策略，一个策略控制多种形态 | 同上 |
| Amorpheus [33] | ICLR 2021 | 用 Transformer 取代图网络做形态无关控制 | 同上 |
| MetaMorph [34] | ICLR 2022 | 大规模形态上训练通用控制器 | 若后续需要统一控制器，可作为方案 |
| ModuMorph [35] | ICML 2023 | 基于上下文调制的通用形态控制 | 同上 |
| Body Transformer [36] | CoRL 2024 | 利用身体拓扑作为注意力偏置 | 同上 |
| URMA [37] | CoRL 2024 | 一个策略控制多种腿足形态 | 同上 |
| GET-Zero [38] | arXiv 2024 | 图嵌入 Transformer，零样本泛化到新具身 | 同上 |

**定位：** 在本项目中，跨形态控制只是基础设施（每个构型可以用独立的简单控制器），不是贡献点。这一节文献用来说明"我们为何不需要通用控制器"。

---

## 6. 跨具身基础模型（VLA / VLN）

| 文献 | 发表 | 核心内容 | 对本项目的意义 |
|---|---|---|---|
| Open X-Embodiment [39] | ICRA 2024 | 22 种机器人的大规模数据集与 RT-X | 跨具身数据范式 |
| Octo [40] / OpenVLA [41] / π0 [42] | RSS 2024 / CoRL 2024 / RSS 2025 | 开源通用机器人策略 | 背景引用 |
| CrossFormer [43] | CoRL 2024 | 一个策略控制机械臂、腿足、无人机、导航机器人 | 同上 |
| HPT [44] | NeurIPS 2024 | 异构预训练 Transformer，用具身专属"茎"对齐 | 同上 |
| X-VLA [45] | ICLR 2026 | 用软提示吸收具身差异的跨具身 VLA | 同上 |
| ★ EMOS [46] | ICLR 2025 | 异构多机器人系统中，LLM 智能体读取"机器人简历"（Robot Resume）来理解各自能力并分配任务 | **本项目"构型简历"的直接来源**；EMOS 在多台固定机器人间选择，我们在一台机器人的多个构型间选择并计入变形代价 |
| NavFoM [47] | ICLR 2026 | 跨具身（四足、无人机、车、人形）导航基础模型 | 把具身差异"泛化掉" |
| RING [48] | arXiv 2024 | 在约百万种随机具身上训练室内导航通才策略 | 同上，可作为学习型对照 |
| CanonNav [49] / Sensor-Layout-Agnostic Nav [50] | arXiv 2026 | 把相机几何差异归一化，使导航行为与相机布局解耦 | 同上 |

**小结：** 这些工作的共同目标是"对身体不敏感"。本项目的论点恰恰相反：当瓶颈来自身体时，敏感地利用身体差异才能看到原本看不到的东西。这个对比可以写进引言作为动机。

---

## 7. 主动视觉、具身问答与视觉搜索

| 文献 | 发表 | 核心内容 | 对本项目的意义 |
|---|---|---|---|
| Agrawal 等 [51] | ICCV 2015 | 用自身运动作为监督学习视觉特征 | 感知与动作耦合的早期深度学习工作 |
| Jayaraman & Grauman [52] | CVPR 2018 | 学习"往哪看"以完成全景观测 | 主动视点选择 |
| ★ Ramakrishnan 等 [53] | Science Robotics 2019 | 通过主动观测补全，涌现出"环顾"探索行为 | 主动感知进入 Science 子刊的代表；动作是视点，不是身体 |
| Yang 等, 具身非模态识别 [54] | ICCV 2019 | 学习移动以识别被遮挡的物体 | 遮挡瓶颈的经典设定，可借鉴其"遮挡"分类 |
| Active Neural SLAM [55] | ICLR 2020 | 模块化探索策略 | 前沿探索基线来源 |
| SemExp [56] | NeurIPS 2020 | 目标导向的语义探索 | 同上 |
| ★ SUGARL [57] | NeurIPS 2023 | 把"感知动作"与"运动动作"分开建模的主动视觉 RL | 与我们最相近的 ML 形式化；但其感知动作是自由的相机，不受身体约束 |
| EQA [58] | CVPR 2018 | 具身问答任务的提出 | 任务形式来源 |
| OpenEQA [59] | CVPR 2024 | 基础模型时代的开放词汇 EQA 基准 | 问题与评测参考 |
| Explore until Confident [60] | RSS 2024 | 用置信度决定何时停止探索 | "何时停"的校准思路可借用到"何时不变形" |
| 3D-Mem [61] / GraphEQA [62] | CVPR 2025 / CoRL 2025 | 用 3D 记忆或场景图进行零样本 EQA | 固定身体的强基线 |
| VLFM [63] | ICRA 2024 | 视觉—语言前沿地图零样本导航 | 前沿基线 |
| Vision in Action [64] | CoRL 2025 | 从人类示范中学习主动"看"的颈部运动 | 主动视觉在操作中的最新进展 |
| Eye, Robot [65] | CoRL 2025 | 可动"眼球"相机，BC-RL 感知—动作闭环 | 同上 |
| E3VS-Bench [66] | arXiv 2026 | 3DGS 场景中依赖视点的主动感知基准 | 相机位姿为动作，传感器与身体解耦 |
| ERGeoBench [67] | arXiv 2026（ICML 2026） | 多模态大模型的具身推理与地理定位基准 | 同上 |
| ★ POSE [68] | arXiv 2026 | 腿足机器人在受限空间中调整身体俯仰/横滚以扩大全向感知 | **最接近的预印本**：用身体姿态服务感知，但身体结构和能力不变，没有机动性代价 |
| ★ VRW [69] | arXiv 2026 | 提出"可见—可达工作空间"指标，指导人形机器人传感器布置 | **概念最接近**：把"能看到"与"能到达"联系起来；但它是设计期离线指标，我们是任务中的在线选择 |
| ActiveScale [70] / SensorPerch [71] | arXiv 2026 | 主动感知的规模化研究 / 传感器布置位置的灵活化 | 近期趋势，建议细读后决定是否引用 |

---

## 8. 视觉语言模型的感知局限

| 文献 | 发表 | 核心内容 | 对本项目的意义 |
|---|---|---|---|
| V* [72] | CVPR 2024 | 引导式视觉搜索，弥补 MLLM 对细节的忽视 | 证明"看不清"是 VLM 的真实瓶颈；它靠图像内放大，我们靠换身体 |
| Eyes Wide Shut [73] | CVPR 2024 | 揭示 CLIP 类视觉编码器的系统性盲点 | 动机：有些信息模型本身看不到，必须换视角 |
| SpatialVLM [74] | CVPR 2024 | 增强 VLM 空间推理 | 语言层的空间理解参考 |
| BLINK [75] | ECCV 2024 | 人类一眼可解、但 MLLM 失败的感知任务 | 同上 |
| DyFo [76] | CVPR 2025 | 免训练的动态聚焦视觉搜索 | 图像内主动感知的上限对照 |
| AdaGlimpse [77] | ECCV 2024 | 任意位置与尺度的主动"瞥视" | 同上 |

**用途：** 这些工作说明"在图像内部做搜索"能解决一部分问题，但当瓶颈是遮挡、高度或视距（物理上不在画面里）时，只能改变观察位置乃至身体。这是我们区分"位姿受限"与"身体受限"两类瓶颈的依据，也是后续机理论文（探针 VLM 是否在内部表示了瓶颈类型）的文献基础。

---

## 9. 机器人自我建模

| 文献 | 发表 | 核心内容 | 对本项目的意义 |
|---|---|---|---|
| Bongard, Zykov, Lipson [78] | Science 2006 | 机器人通过持续自我建模在损伤后恢复 | 自我模型的经典工作 |
| Cully 等 [79] | Nature 2015 | 预先构建行为—性能地图，损伤后快速适应 | **能力地图的直接先例**：我们的"能力图谱"是"构型 → 可达感知能力"的地图 |
| Kwiatkowski & Lipson [80] | Science Robotics 2019 | 任务无关的自我建模 | 同上 |
| Chen 等 [81] | Science Robotics 2022 | 全身视觉自我建模 | 同上 |
| 自我发现身体形态 [82] | Science Robotics 2023 | 机器学习驱动机器人自行发现身体形态 | 同上 |
| 自建仿真 [83] | Nat. Mach. Intell. 2025 | 机器人仅凭视觉学会构建自身的仿真模型 | 同上；未来真机阶段可用来自动获得构型的能力边界 |

**定位：** 本项目的"构型简历 + 能力图谱"可被理解为一种显式的、面向感知的自我模型。引用这一线可以把我们的工作放进 Science / Nature 系期刊熟悉的叙事中。

---

## 10. 传感器布置与次模优化

| 文献 | 发表 | 核心内容 | 对本项目的意义 |
|---|---|---|---|
| Krause, Singh, Guestrin [84] | JMLR 2008 | 高斯过程下近最优的传感器布置（次模性） | 构型库选择用贪心覆盖的理论依据 |
| Golovin & Krause [85] | JAIR 2011 | 自适应次模性：贪心自适应策略的近最优保证 | 在线"是否变形"决策的理论框架参考 |
| Norouzi 等 [86] | JIRS 2017 | 可重构机器人在不平地形上兼顾稳定性的路径规划 | 机器人学中"重构—稳定性"耦合的先例 |

---

## 11. 仿真与运动控制基础

| 文献 | 发表 | 核心内容 | 对本项目的意义 |
|---|---|---|---|
| MuJoCo [87] | IROS 2012 | 物理引擎 | 实现平台 |
| Hwangbo 等 [88] / Lee 等 [89] / Miki 等 [90] | Science Robotics 2019 / 2020 / 2022 | 仿真训练腿足控制、地形泛化、感知型运动 | 腿足控制背景；说明姿态与感知已被联合考虑但未涉及变形 |
| Rudin 等 [91] | CoRL 2021 | 大规模并行 RL 数分钟学会行走 | 若需训练构型控制器 |
| MuJoCo Playground [92] | arXiv 2025 | GPU 加速的 MuJoCo 机器人学习框架 | 同上 |
| MolmoSpaces [93] | arXiv 2026 | 大规模 MJCF 室内场景，带物体元数据 | 场景来源 |
| Habitat [94] / ProcTHOR [95] | ICCV 2019 / NeurIPS 2022 | 具身 AI 仿真平台 / 程序化场景生成 | 背景引用 |

---

## 12. 综合：研究空白与本项目定位

### 12.1 维度对比

| 工作类别 | 传感器位姿可动 | 身体构型在线改变 | 改变是为了感知 | 建模能力耦合 | 实测变形代价 | 会选择"不变形" |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| 主动视觉 / EQA [53–63] | ✓ | ✗ | — | ✗ | ✗ | ✗ |
| 视点 / 变焦基准 [66, 67] | ✓ | ✗ | — | ✗ | ✗ | ✗ |
| 变形机器人（运动）[16, 17, 19, 21] | ✗ | ✓ | ✗ | 部分 | 部分 | ✗ |
| 在线变形 RL [23, 27] | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| 感知驱动重构 [15] | ✓ | ✓ | ✗（为执行） | ✗ | ✗ | ✗ |
| 姿态服务感知 POSE [68] | ✓ | 仅姿态 | ✓ | ✗ | ✗ | ✗ |
| 设计期可见—可达 VRW [69] | — | 设计期 | ✓ | ✓ | ✗ | — |
| 跨具身基础模型 [45, 47–50] | — | 视为干扰 | ✗ | ✗ | ✗ | ✗ |
| **本项目** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### 12.2 与 C1–C4 主张的对应

- **C1 存在性（变形确实扩展了可见集合）：** 需要与 [1–3] 的主动感知理论、[69] 的可见—可达概念、[6] 的生物学先例对话。
- **C2 归因（区分位姿受限与身体受限）：** 需要与 [54]（遮挡）、[72–77]（图像内搜索的上限）对比，说明哪些瓶颈只有换身体才能解决。
- **C3 决策（何时变、变成什么、何时不变）：** 需要与 [57]（感知/运动分离的 RL）、[60]（置信度停止）、[85]（自适应次模性）、[46]（简历式能力推理）对比。
- **C4 物理有效性（变形代价与稳定性实测）：** 需要与 [21]、[86] 以及 [88–90] 的腿足控制文献对话。

### 12.3 审稿人可能的质疑与对应文献

| 质疑 | 回应思路 | 关键文献 |
|---|---|---|
| "这只是换了个更高的相机" | 自由相机作为上界基线，说明真实身体约束下的取舍才是问题本身 | [57, 66] |
| "Daudelin 2018 已经做过感知驱动重构" | 方向相反：它为执行任务而重构，我们为获取证据而重构，并计入机动性损失 | [15] |
| "POSE 也用身体姿态做感知" | 姿态不改变能力集合；我们的构型会让某些动作不可达 | [68] |
| "跨具身模型可以泛化掉身体差异" | 泛化掉的正是我们需要的信息 | [45, 47–50] |

---

## 13. 建议精读顺序（12 篇）

1. Daudelin 等 2018 [15]：最需要区分的工作
2. Learning to Reconfigure 2026 [21]：基础设施来源
3. POSE [68] 与 VRW [69]：最近的竞争者
4. EMOS [46]：简历式能力推理
5. SUGARL [57]：感知动作的形式化
6. Pathak 等 2019 [23] 与 DittoGym [27]：在线变形的 ML 先例
7. Cully 等 2015 [79]：能力地图
8. Bajcsy 等 2018 [3]：理论框架
9. Golovin & Krause 2011 [85]：决策理论
10. Explore until Confident [60]：何时停止
11. Baines 等 2022 [16]：顶刊变形机器人叙事
12. 可重构模块腿 PNAS [19]：硬件形态最接近

---

## 参考文献

### 主动感知与认知科学
1. R. Bajcsy. Active perception. *Proceedings of the IEEE*, 76(8):966–1005, 1988. https://doi.org/10.1109/5.5968
2. J. Aloimonos, I. Weiss, A. Bandyopadhyay. Active vision. *International Journal of Computer Vision*, 1(4):333–356, 1988. https://doi.org/10.1007/BF00133571
3. R. Bajcsy, Y. Aloimonos, J. K. Tsotsos. Revisiting active perception. *Autonomous Robots*, 42:177–196, 2018. https://doi.org/10.1007/s10514-017-9615-3
4. J. K. O'Regan, A. Noë. A sensorimotor account of vision and visual consciousness. *Behavioral and Brain Sciences*, 24(5):939–973, 2001. https://doi.org/10.1017/S0140525X01000115
5. J. Gottlieb, P.-Y. Oudeyer. Towards a neuroscience of active sampling and curiosity. *Nature Reviews Neuroscience*, 19:758–770, 2018. https://doi.org/10.1038/s41583-018-0078-0
6. M. A. MacIver, L. Schmitz, U. Mugan, T. D. Murphey, C. D. Mobley. Massive increase in visual range preceded the origin of terrestrial vertebrates. *PNAS*, 114(12):E2375–E2384, 2017. https://doi.org/10.1073/pnas.1615563114

### 具身智能与形态
7. R. Pfeifer, M. Lungarella, F. Iida. Self-organization, embodiment, and biologically inspired robotics. *Science*, 318:1088–1093, 2007. https://doi.org/10.1126/science.1145803
8. A. Gupta, S. Savarese, S. Ganguli, L. Fei-Fei. Embodied intelligence via learning and evolution. *Nature Communications*, 12:5721, 2021. https://doi.org/10.1038/s41467-021-25874-z
9. S. Kriegman, D. Blackiston, M. Levin, J. Bongard. A scalable pipeline for designing reconfigurable organisms. *PNAS*, 117(4):1853–1859, 2020. https://doi.org/10.1073/pnas.1910837117
10. K. Sims. Evolving virtual creatures. *SIGGRAPH*, 1994. https://doi.org/10.1145/192161.192167

### 变形、可重构与模块化机器人
11. M. Yim, W.-M. Shen, B. Salemi, D. Rus, M. Moll, H. Lipson, E. Klavins, G. S. Chirikjian. Modular self-reconfigurable robot systems: challenges and opportunities for the future. *IEEE Robotics & Automation Magazine*, 14(1):43–52, 2007. https://doi.org/10.1109/MRA.2007.339623
12. V. Zykov, E. Mytilinaios, B. Adams, H. Lipson. Self-reproducing machines. *Nature*, 435:163–164, 2005. https://doi.org/10.1038/435163a
13. M. Rubenstein, A. Cornejo, R. Nagpal. Programmable self-assembly in a thousand-robot swarm. *Science*, 345:795–799, 2014. https://doi.org/10.1126/science.1254295
14. S. Li, R. Batra, D. Brown, et al. Particle robotics based on statistical mechanics of loosely coupled components. *Nature*, 567:361–365, 2019. https://doi.org/10.1038/s41586-019-1022-9
15. J. Daudelin, G. Jing, T. Tosun, M. Yim, H. Kress-Gazit, M. Campbell. An integrated system for perception-driven autonomy with modular robots. *Science Robotics*, 3(23):eaat4983, 2018. https://www.science.org/doi/full/10.1126/scirobotics.aat4983
16. R. Baines, S. K. Patiballa, J. Booth, et al. Multi-environment robotic transitions through adaptive morphogenesis. *Nature*, 610:283–289, 2022. https://www.nature.com/articles/s41586-022-05188-w
17. E. Sihite, A. Kalantari, R. Nemovi, A. Ramezani, M. Gharib. Multi-Modal Mobility Morphobot (M4) with appendage repurposing for locomotion plasticity enhancement. *Nature Communications*, 14:3323, 2023. https://www.nature.com/articles/s41467-023-39018-y
18. Material-like robotic collectives with spatiotemporal control of strength and shape. *Science*, 2025. https://www.science.org/doi/10.1126/science.ads7942
19. Agile legged locomotion in reconfigurable modular robots. *PNAS*, 2025. https://www.pnas.org/doi/10.1073/pnas.2519129123 ；预印本 https://arxiv.org/abs/2505.00784
20. D. Shah, B. Yang, S. Kriegman, M. Levin, J. Bongard, R. Kramer-Bottiglio. Shape changing robots: bioinspiration, simulation, and physical realization. *Advanced Materials*, 33:2002882, 2021. https://doi.org/10.1002/adma.202002882
21. Learning to Reconfigure: Co-designing reconfigurable robots for heterogeneous locomotion. *ICML*, 2026. https://icml.cc/virtual/2026/poster/61720 ；项目页 https://ltrweb.github.io/learning_to_reconfigure/ ；代码 https://github.com/Xiaoyu-Xiong/Learning-to-Reconfig

### 形态协同设计
22. T. Wang, Y. Zhou, S. Fidler, J. Ba. Neural graph evolution: towards efficient automatic robot design. *ICLR*, 2019. https://arxiv.org/abs/1906.05370
23. D. Pathak, C. Lu, T. Darrell, P. Isola, A. A. Efros. Learning to control self-assembling morphologies: a study of generalization via modularity. *NeurIPS*, 2019. https://proceedings.neurips.cc/paper/2019/hash/c26820b8a4c1b3c2aa868d6d57e14a79-Abstract.html
24. Y. Yuan, Y. Song, Z. Luo, W. Sun, K. Kitani. Transform2Act: learning a transform-and-control policy for efficient agent design. *ICLR*, 2022. https://arxiv.org/abs/2110.03659
25. J. Bhatia, H. Jackson, Y. Tian, J. Xu, W. Matusik. Evolution Gym: a large-scale benchmark for evolving soft robots. *NeurIPS*, 2021. https://arxiv.org/abs/2201.09863
26. T.-H. Wang, P. Ma, A. E. Spielberg, et al. SoftZoo: a soft robot co-design benchmark for locomotion in diverse environments. *ICLR*, 2023. https://iclr.cc/virtual/2023/poster/11093
27. S. Huang, B. Chen, H. Xu, V. Sitzmann. DittoGym: learning to control soft shape-shifting robots. *ICLR*, 2024. https://arxiv.org/abs/2401.13231
28. H. Lu, et al. BodyGen: advancing towards efficient embodiment co-design. *ICLR*, 2025. https://arxiv.org/abs/2503.00533
29. A. Zhao, J. Xu, M. Konaković-Luković, J. Hughes, A. Spielberg, D. Rus, W. Matusik. RoboGrammar: graph grammar for terrain-optimized robot design. *ACM Transactions on Graphics (SIGGRAPH Asia)*, 39(6), 2020. https://doi.org/10.1145/3414685.3417831
30. D. Ha. Reinforcement learning for improving agent design. *Artificial Life*, 25(4):352–365, 2019. https://arxiv.org/abs/1810.03779

### 形态无关控制
31. T. Wang, R. Liao, J. Ba, S. Fidler. NerveNet: learning structured policy with graph neural networks. *ICLR*, 2018. https://openreview.net/forum?id=S1sqHMZCb
32. W. Huang, I. Mordatch, D. Pathak. One policy to control them all: shared modular policies for agent-agnostic control. *ICML*, 2020. https://arxiv.org/abs/2007.04976
33. V. Kurin, M. Igl, T. Rocktäschel, W. Böhmer, S. Whiteson. My body is a cage: the role of morphology in graph-based incompatible control. *ICLR*, 2021. https://arxiv.org/abs/2010.01856
34. A. Gupta, L. Fan, S. Ganguli, L. Fei-Fei. MetaMorph: learning universal controllers with transformers. *ICLR*, 2022. https://arxiv.org/abs/2203.11931
35. Z. Xiong, J. Beck, S. Whiteson. Universal morphology control via contextual modulation. *ICML*, 2023. https://arxiv.org/abs/2302.11070
36. C. Sferrazza, D.-M. Huang, F. Liu, J. Lee, P. Abbeel. Body Transformer: leveraging robot embodiment for policy learning. *CoRL*, 2024. https://proceedings.mlr.press/v270/sferrazza25a.html
37. N. Bohlinger, et al. One policy to run them all: an end-to-end learning approach to multi-embodiment locomotion. *CoRL*, 2024. https://arxiv.org/abs/2409.06366
38. A. Patel, S. Song. GET-Zero: graph embodiment transformer for zero-shot embodiment generalization. arXiv:2407.15002, 2024. https://arxiv.org/abs/2407.15002

### 跨具身基础模型
39. Open X-Embodiment Collaboration. Open X-Embodiment: robotic learning datasets and RT-X models. *ICRA*, 2024. https://arxiv.org/abs/2310.08864
40. Octo Model Team. Octo: an open-source generalist robot policy. *RSS*, 2024. https://arxiv.org/abs/2405.12213
41. M. J. Kim, et al. OpenVLA: an open-source vision-language-action model. *CoRL*, 2024. https://arxiv.org/abs/2406.09246
42. K. Black, et al. π0: a vision-language-action flow model for general robot control. *RSS*, 2025. https://arxiv.org/abs/2410.24164
43. R. Doshi, H. Walke, O. Mees, S. Dasari, S. Levine. Scaling cross-embodied learning: one policy for manipulation, navigation, locomotion and aviation (CrossFormer). *CoRL*, 2024. https://arxiv.org/abs/2408.11812
44. L. Wang, X. Chen, J. Zhao, K. He. Scaling proprioceptive-visual learning with heterogeneous pre-trained transformers (HPT). *NeurIPS*, 2024. https://arxiv.org/abs/2409.20537
45. X-VLA: soft-prompted transformer as scalable cross-embodiment vision-language-action model. *ICLR*, 2026. https://iclr.cc/virtual/2026/poster/10007740
46. J. Chen, C. Yu, X. Zhou, et al. EMOS: embodiment-aware heterogeneous multi-robot operating system with LLM agents. *ICLR*, 2025. https://arxiv.org/abs/2410.22662
47. J. Zhang, et al. Embodied navigation foundation model (NavFoM). *ICLR*, 2026. https://proceedings.iclr.cc/paper_files/paper/2026/hash/ceb45c48e29e7f49b0b47edb98e43691-Abstract-Conference.html ；项目页 https://pku-epic.github.io/NavFoM-Web/
48. A. Eftekhar, et al. The One RING: a robotic indoor navigation generalist. arXiv:2412.14401, 2024. https://arxiv.org/abs/2412.14401
49. CanonNav: disentangling navigation behavior from camera geometry in cross-platform visual navigation. arXiv:2608.30242, 2026. https://arxiv.org/abs/2608.30242
50. Sensor-layout-agnostic navigation. arXiv:2610.08306, 2026. https://arxiv.org/abs/2610.08306

### 主动视觉、具身问答与视觉搜索
51. P. Agrawal, J. Carreira, J. Malik. Learning to see by moving. *ICCV*, 2015. https://arxiv.org/abs/1505.01596
52. D. Jayaraman, K. Grauman. Learning to look around: intelligently exploring unseen environments for unknown tasks. *CVPR*, 2018. https://arxiv.org/abs/1709.00507
53. S. K. Ramakrishnan, D. Jayaraman, K. Grauman. Emergence of exploratory look-around behaviors through active observation completion. *Science Robotics*, 4(30):eaaw6326, 2019. https://www.science.org/doi/10.1126/scirobotics.aaw6326
54. J. Yang, Z. Ren, M. Xu, X. Chen, D. Crandall, D. Parikh, D. Batra. Embodied amodal recognition: learning to move to perceive objects. *ICCV*, 2019. https://openaccess.thecvf.com/content_ICCV_2019/html/Yang_Embodied_Amodal_Recognition_Learning_to_Move_to_Perceive_Objects_ICCV_2019_paper.html
55. D. S. Chaplot, D. Gandhi, S. Gupta, A. Gupta, R. Salakhutdinov. Learning to explore using active neural SLAM. *ICLR*, 2020. https://arxiv.org/abs/2004.05155
56. D. S. Chaplot, D. Gandhi, A. Gupta, R. Salakhutdinov. Object goal navigation using goal-oriented semantic exploration. *NeurIPS*, 2020. https://arxiv.org/abs/2007.00643
57. J. Shang, M. S. Ryoo. Active vision reinforcement learning under limited visual observability (SUGARL). *NeurIPS*, 2023. https://arxiv.org/abs/2306.00975
58. A. Das, S. Datta, G. Gkioxari, S. Lee, D. Parikh, D. Batra. Embodied question answering. *CVPR*, 2018. https://arxiv.org/abs/1711.11543
59. A. Majumdar, et al. OpenEQA: embodied question answering in the era of foundation models. *CVPR*, 2024. https://openaccess.thecvf.com/content/CVPR2024/papers/Majumdar_OpenEQA_Embodied_Question_Answering_in_the_Era_of_Foundation_Models_CVPR_2024_paper.pdf
60. A. Z. Ren, J. Clark, A. Dixit, M. Itkina, A. Majumdar, D. Sadigh. Explore until confident: efficient exploration for embodied question answering. *RSS*, 2024. https://www.roboticsproceedings.org/rss20/p089.pdf
61. Y. Yang, et al. 3D-Mem: 3D scene memory for embodied exploration and reasoning. *CVPR*, 2025. https://arxiv.org/abs/2411.17735
62. S. Saxena, et al. GraphEQA: using 3D semantic scene graphs for real-time embodied question answering. *CoRL*, 2025. https://arxiv.org/abs/2412.14480
63. N. Yokoyama, S. Ha, D. Batra, J. Wang, B. Bucher. VLFM: vision-language frontier maps for zero-shot semantic navigation. *ICRA*, 2024. https://arxiv.org/abs/2312.03275
64. H. Xiong, et al. Vision in Action: learning active perception from human demonstrations. *CoRL*, 2025. https://arxiv.org/abs/2506.15666
65. J. Kerr, et al. Eye, Robot: learning to look to act with a BC-RL perception-action loop. *CoRL*, 2025. https://proceedings.mlr.press/v305/kerr25a.html
66. E3VS-Bench: a benchmark for viewpoint-dependent active perception in 3D Gaussian splatting scenes. arXiv:2604.17969, 2026. https://arxiv.org/abs/2604.17969
67. ERGeoBench: a comprehensive benchmark for embodied reasoning and geo-localization in multimodal large language models. arXiv:2605.31251, 2026. https://arxiv.org/abs/2605.31251
68. POSE: pose-aware legged robot semantic exploration with omnidirectional perception in confined unknown environments. arXiv:2609.19460, 2026. https://arxiv.org/abs/2609.19460
69. Visible-reachable workspace for perception-aware humanoid design. arXiv:2609.08905, 2026. https://arxiv.org/abs/2609.08905
70. ActiveScale: scaling active perception for robots across model, data, and hardware. arXiv:2609.18514, 2026. https://arxiv.org/abs/2609.18514
71. SensorPerch: sense wherever and whenever it matters. arXiv:2607.10682, 2026. https://arxiv.org/abs/2607.10682

### 视觉语言模型的感知局限
72. P. Wu, S. Xie. V*: guided visual search as a core mechanism in multimodal LLMs. *CVPR*, 2024. https://arxiv.org/abs/2312.14135
73. S. Tong, Z. Liu, Y. Zhai, Y. Ma, Y. LeCun, S. Xie. Eyes wide shut? Exploring the visual shortcomings of multimodal LLMs. *CVPR*, 2024. https://arxiv.org/abs/2401.06209
74. B. Chen, et al. SpatialVLM: endowing vision-language models with spatial reasoning capabilities. *CVPR*, 2024. https://arxiv.org/abs/2401.12168
75. X. Fu, et al. BLINK: multimodal large language models can see but not perceive. *ECCV*, 2024. https://arxiv.org/abs/2404.12390
76. G. Li, et al. DyFo: a training-free dynamic focus visual search for enhancing LMMs in fine-grained visual understanding. *CVPR*, 2025. https://openaccess.thecvf.com/content/CVPR2025/html/Li_DyFo_A_Training-Free_Dynamic_Focus_Visual_Search_for_Enhancing_LMMs_CVPR_2025_paper.html
77. A. Pardyl, et al. AdaGlimpse: active visual exploration with arbitrary glimpse position and scale. *ECCV*, 2024. https://arxiv.org/abs/2404.03482

### 机器人自我建模
78. J. Bongard, V. Zykov, H. Lipson. Resilient machines through continuous self-modeling. *Science*, 314:1118–1121, 2006. https://doi.org/10.1126/science.1133687
79. A. Cully, J. Clune, D. Tarapore, J.-B. Mouret. Robots that can adapt like animals. *Nature*, 521:503–507, 2015. https://www.nature.com/articles/nature14422
80. R. Kwiatkowski, H. Lipson. Task-agnostic self-modeling machines. *Science Robotics*, 4(26):eaau9354, 2019. https://doi.org/10.1126/scirobotics.aau9354
81. B. Chen, R. Kwiatkowski, C. Vondrick, H. Lipson. Fully body visual self-modeling of robot morphologies. *Science Robotics*, 7(68):eabn1944, 2022. https://doi.org/10.1126/scirobotics.abn1944 ；预印本 https://arxiv.org/abs/2111.06389
82. Machine learning–driven self-discovery of the robot body morphology. *Science Robotics*, 2023. https://www.science.org/doi/10.1126/scirobotics.adh0972
83. Teaching robots to build simulations of themselves. *Nature Machine Intelligence*, 2025. https://www.nature.com/articles/s42256-025-01006-w ；预印本 https://arxiv.org/abs/2311.12151

### 传感器布置与次模优化
84. A. Krause, A. Singh, C. Guestrin. Near-optimal sensor placements in Gaussian processes: theory, efficient algorithms and empirical studies. *JMLR*, 9:235–284, 2008. https://www.jmlr.org/papers/v9/krause08a.html
85. D. Golovin, A. Krause. Adaptive submodularity: theory and applications in active learning and stochastic optimization. *JAIR*, 42:427–486, 2011. https://arxiv.org/abs/1003.3967
86. M. Norouzi, J. V. Miró, G. Dissanayake. Planning stable and efficient paths for reconfigurable robots on uneven terrain. *Journal of Intelligent & Robotic Systems*, 2017. https://link.springer.com/article/10.1007/s10846-017-0495-8

### 仿真与运动控制
87. E. Todorov, T. Erez, Y. Tassa. MuJoCo: a physics engine for model-based control. *IROS*, 2012. https://doi.org/10.1109/IROS.2012.6386109
88. J. Hwangbo, et al. Learning agile and dynamic motor skills for legged robots. *Science Robotics*, 4(26):eaau5872, 2019. https://doi.org/10.1126/scirobotics.aau5872
89. J. Lee, J. Hwangbo, L. Wellhausen, V. Koltun, M. Hutter. Learning quadrupedal locomotion over challenging terrain. *Science Robotics*, 5(47):eabc5986, 2020. https://doi.org/10.1126/scirobotics.abc5986
90. T. Miki, et al. Learning robust perceptive locomotion for quadrupedal robots in the wild. *Science Robotics*, 7(62):eabk2822, 2022. https://doi.org/10.1126/scirobotics.abk2822
91. N. Rudin, D. Hoeller, P. Reist, M. Hutter. Learning to walk in minutes using massively parallel deep reinforcement learning. *CoRL*, 2021. https://arxiv.org/abs/2109.11978
92. K. Zakka, et al. MuJoCo Playground. arXiv:2502.08844, 2025. https://arxiv.org/abs/2502.08844
93. MolmoSpaces. arXiv:2602.11337, 2026. https://arxiv.org/abs/2602.11337
94. M. Savva, et al. Habitat: a platform for embodied AI research. *ICCV*, 2019. https://arxiv.org/abs/1904.01201
95. M. Deitke, et al. ProcTHOR: large-scale embodied AI using procedural generation. *NeurIPS*, 2022. https://arxiv.org/abs/2206.06994

---

## 核实说明

- **本轮已用检索结果核对了标题、期刊/会议与链接的条目：** [6] [15] [16] [17] [18] [19] [21] [23] [26] [27] [36] [45] [47] [53] [54] [57] [59] [60] [63] [64] [65] [66] [67] [68] [69] [70] [71] [76] [77] [79] [82] [83] [86]，以及 [38] 的 arXiv 编号。
- **依据记忆写出、把握较高但未逐一点开核对的条目：** 经典文献 [1–5] [7–14] [20] [22] [24] [25] [30–35] [37] [39–44] [51] [52] [55] [56] [58] [72–75] [78] [80] [81] [84] [85] [87–91] [94] [95] 的作者、卷期、页码与 arXiv 编号。投稿前请用 Google Scholar 或 DBLP 统一导出 BibTeX 覆盖。
- **作者列表留空或不全的条目：** [18] [19] [21] [45] [82] [83] 以及若干 "et al."，原因是本轮未能打开原文页面确认作者顺序。
- **需要特别留意：**
  - [19] 的期刊页显示为 PNAS，DOI 编号前缀为 2519129123，年份按预印本与报道推定为 2025–2026，请以期刊页为准。
  - [21] Learning to Reconfigure 在 ICML 2026 会议页上的标题为 *Co-designing Reconfigurable robots for Heterogeneous Locomotion*。
  - [50] 的标题沿用此前 RELATED_REPOS.md 中的记录，本轮未能通过编号检索复核。
  - [67] 的 ICML 2026 录用信息来自此前对话，本轮仅确认了 arXiv 版本。
  - [86] 的标题依据记忆，链接已在先前检索中确认。
- **刻意未收录：** CuCo（ICLR 2023，未能确认）、一篇约 2012 年的"可重构机器人高可见性稳定路径"论文（作者与出处未能确认，用 [86] 替代）、HuG（arXiv 2611.01659，未能确认内容）、协同设计综述 arXiv 2512.04770（未能确认标题）。
