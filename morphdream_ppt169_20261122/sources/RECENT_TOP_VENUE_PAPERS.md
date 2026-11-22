# 近两年顶会相关工作（2025–2026，侧重开源）

> 本文是 LITERATURE_REVIEW.md 的补充，只收 2025–2026 年（含 2024 年底的 CoRL）发表在 ICML、ICLR、NeurIPS、CVPR、ICCV、AAAI、ACM MM、IJCAI、RSS、CoRL、ICRA、IROS 上、与"变形感知"相关的工作。最后单列几篇尚未录用、但与本项目非常接近的 2026 年预印本。
>
> 检索日期：2026-11-17。
>
> **代码标记：**
> - 🟢：GitHub 仓库已确认存在，并能拉取（git ls-remote）。
> - 🟡：只有项目页或匿名仓库，或者作者声明"即将发布"。
> - ⚪：没有找到代码。
>
> ★ 表示与本项目最相关、写相关工作时要正面区分。

---

## 0. 要点

1. **"让大模型自己决定往哪看"是 2025–2026 年最热的方向之一，但动作仍然只是相机。** 代表工作有 Active-o3（ICML 2026）、I-Perceive 与 ActiveZero（NeurIPS 2026）、SaPaVe 与 ActiveVLA（CVPR 2026）、Sea2（ICML 2026）。它们控制的是相机位姿、云台或图像内区域，身体构型始终不变。
2. **多篇工作独立发现了同一个现象：模型知道自己缺信息，却不会去拿。**
   - PhysVLM-AVR（NeurIPS 2025）：具身大模型能察觉信息缺失，但难以主动获取。
   - Theory of Space（ICLR 2026）：模型自己探索时，比直接给它观测结果表现更差。
   - TVRBench（2026 预印本）：只需原地转头时尚可；一旦必须移动身体，成功率大幅下降。

   这三条证据可以直接作为我们机理论文（"会诊断瓶颈 ≠ 会选择身体"）的动机。
3. **PhysVLM（CVPR 2025）是"把机器人能力喂给 VLM"的直接先例。** 它把机器人可达空间投影成图像中的灰色遮罩，作为 VLM 的额外输入。我们的"构型能力图谱"可以用同样的方式提供给语言层。
4. **形态协同设计在 ICLR / ICML / NeurIPS 持续活跃，目标全部是运动或操作性能。** 2025–2026 年至少有 10 篇，多数已开源，但没有一篇把感知收益作为目标。
5. **跨具身工作继续把身体差异视为要消除的"差距"。** VLN-PE（ICCV 2025）实测发现，人形、四足、轮式机器人上的导航性能明显下降，原因之一是"受限的观测空间"。这正好是本项目要利用的现象。
6. **AAAI、IJCAI、ACM MM 上直接相关的工作很少。** 只找到 All-Angles Bench（AAAI 2026）和 EvoAgent（MM 2025），IJCAI 2025–2026 没有找到。ICRA 和 IROS 上的相关工作多是硬件或下一最佳视点（NBV）规划，不涉及"形态—感知"决策。

---

## 1. 大模型的主动感知：决定往哪看

| 论文 | 会议 | 代码 | 做了什么 | 对本项目 |
|---|---|---|---|---|
| ★ **Active-o3** [论文](https://arxiv.org/abs/2505.21457) · [会议页](https://icml.cc/virtual/2026/poster/66636) | ICML 2026 | 🟢 [aim-uofa/Active-o3](https://github.com/aim-uofa/Active-o3) | 用 GRPO 强化学习训练多模态大模型主动选择要放大观察的区域 | 奖励设计与训练流程可借鉴；但动作是图像内区域，不涉及身体 |
| **Sea2**（See, Act, Adapt）[会议页](https://icml.cc/virtual/2026/poster/65692) · [arXiv](https://arxiv.org/abs/2602.23806) | ICML 2026 | ⚪ | 把 VLM 变成相机位姿控制器，移向更有信息量的视点；强化学习奖励来自冻结感知模块的置信度变化，无需真值标签 | **"用感知置信度变化当奖励"** 可直接用作我们的证据收益信号 |
| **I-Perceive** [会议页](https://neurips.cc/virtual/2026/poster/149023) · [arXiv](https://arxiv.org/abs/2603.00600) | NeurIPS 2026 | 🟡 [项目页](https://roboticsjtu.github.io/I-Perceive-Page/) | 根据语言指令直接预测满足感知目标的 6D 相机位姿，并构建了大规模"语言—视点"数据集 | 相当于"自由相机"上界；我们的构型选择可看作受身体约束的 I-Perceive |
| ★ **PhysVLM-AVR** [会议页](https://neurips.cc/virtual/2025/poster/119450) · [arXiv](https://arxiv.org/abs/2510.21111) | NeurIPS 2025 | ⚪ | 提出主动视觉推理任务与 CLEVR-AVR 基准；发现具身大模型能察觉信息缺失，但难以主动获取 | **机理论文的直接动机**："察觉"与"行动"之间存在鸿沟 |
| ★ **Theory of Space** [会议页](https://www.iclr.cc/virtual/2026/poster/10011179) · [arXiv](https://arxiv.org/abs/2602.07055) | ICLR 2026 | 🟢 [mll-lab-nu/Theory-of-Space](https://github.com/mll-lab-nu/Theory-of-Space) | 比较大模型"自己探索"与"直接给观测"两种设定：前者更差、探索冗余；通过信念探测发现，瓶颈在感知错误和信念更新不稳定 | 它的**信念探测方法**可直接借鉴到我们的探针实验 |
| **MindCube** [会议页](https://iclr.cc/virtual/2026/poster/10011954) · [arXiv](https://arxiv.org/abs/2506.21458) | ICLR 2026 | 🟢 [mll-lab-nu/MindCube](https://github.com/mll-lab-nu/MindCube) | 评测大模型能否从少量视角构建空间心智模型；先生成认知地图再推理能明显提升效果 | 我们"看不到"的问题可分为"视角不足"和"身体受限"两类；它只覆盖前者 |
| **MindJourney** [会议页](https://neurips.cc/virtual/2025/poster/118581) · [arXiv](https://arxiv.org/abs/2507.12508) | NeurIPS 2025 | 🟢 [UMass-Embodied-AGI/MindJourney](https://github.com/UMass-Embodied-AGI/MindJourney) | 测试时让 VLM 借助视频世界模型"想象"相机移动后的画面，再回答空间问题 | "想象换视角"的替代方案；可作为"不实际变形、只靠想象"的对照基线 |
| **GenEx** [会议页](https://iclr.cc/virtual/2025/poster/30770) · [arXiv](https://arxiv.org/abs/2412.09624) | ICLR 2025 | 🟢 [GenEx-world/GenEx](https://github.com/GenEx-world/GenEx) | 从单张图生成可探索的 3D 世界，智能体通过想象探索来辅助决策 | 同上 |
| **VSI-Bench**（Thinking in Space）[论文](https://openaccess.thecvf.com/content/CVPR2025/html/Yang_Thinking_in_Space_How_Multimodal_Large_Language_Models_See_Remember_CVPR_2025_paper.html) | CVPR 2025 | 🟢 [vision-x-nyu/thinking-in-space](https://github.com/vision-x-nyu/thinking-in-space) | 视频空间智能基准：测大模型如何看、记、回忆空间 | 题型设计可参考 |
| **All-Angles Bench** [arXiv](https://arxiv.org/abs/2504.15280) | AAAI 2026 | 🟢 [danielchyeh/All-Angles-Bench](https://github.com/danielchyeh/All-Angles-Bench) | 评测大模型的多视角理解，发现跨视角对应和相机位姿估计较弱 | 说明多视角融合本身也是瓶颈，换身体后需要正确融合新旧视角 |
| **VG-AVS** [页面](https://icml.cc/virtual/2026/78164) · [arXiv](https://arxiv.org/abs/2512.13250) | ICML 2026 **研讨会** | ⚪ | 在 EQA 末端只根据当前画面微调视点，证据足够就停止；SFT 之后再做强化学习 | "何时停"的学习方式可参考；注意这是研讨会论文 |
| **NavBench** [会议页](https://neurips.cc/virtual/2025/poster/116120) · [arXiv](https://arxiv.org/abs/2506.01031) | NeurIPS 2025 | ⚪ | 探测大模型的具身导航能力 | 评测设计参考 |

---

## 2. 具身问答与探索：固定身体的强基线

| 论文 | 会议 | 代码 | 做了什么 | 对本项目 |
|---|---|---|---|---|
| **MTU3D** [论文](https://openaccess.thecvf.com/content/ICCV2025/html/Zhu_Move_to_Understand_a_3D_Scene_Bridging_Visual_Grounding_and_ICCV_2025_paper.html) | ICCV 2025 | 🟢 [MTU3D/MTU3D](https://github.com/MTU3D/MTU3D) | 把视觉定位与前沿探索统一到一个模型中 | 固定身体基线 |
| **EXPRESS-Bench** [论文](https://openaccess.thecvf.com/content/ICCV2025/html/Jiang_Beyond_the_Destination_A_Novel_Benchmark_for_Exploration-Aware_Embodied_Question_ICCV_2025_paper.html) | ICCV 2025 | 🟢 [HCPLab-SYSU/EXPRESS-Bench](https://github.com/HCPLab-SYSU/EXPRESS-Bench) | 考察探索过程本身是否支撑答案；评价"探索—答案一致性" | 我们的"证据是否来自正确视角"可借用这类一致性指标 |
| **3D-Mem** [论文](https://openaccess.thecvf.com/content/CVPR2025/html/Yang_3D-Mem_3D_Scene_Memory_for_Embodied_Exploration_and_Reasoning_CVPR_2025_paper.html) | CVPR 2025 | 🟢 [UMass-Embodied-AGI/3D-Mem](https://github.com/UMass-Embodied-AGI/3D-Mem) | 用快照式 3D 场景记忆做探索与推理 | 固定身体基线（已在计划中） |
| **GraphEQA** [arXiv](https://arxiv.org/abs/2412.14480) | CoRL 2025 | 🟢 [SaumyaSaxena/graph_eqa](https://github.com/SaumyaSaxena/graph_eqa) | 用实时 3D 场景图做 EQA | 固定身体基线 |
| **Predict Before You Explore** [会议页](https://cvpr.thecvf.com/virtual/2026/poster/37489) | CVPR 2026 | ⚪ | 先预测再探索，并使用专用记忆 | 背景引用 |
| **Prune-Then-Plan** [项目页](https://noahfrahm.github.io/Prune-Then-Plan-project-page) · [arXiv](https://arxiv.org/abs/2511.19768) | CVPR 2026 Findings | 🟢 [noahfrahm/Prune-Then-Plan](https://github.com/noahfrahm/Prune-Then-Plan) | 对前沿探索做逐步置信度校准，减少来回摇摆 | 校准方法可用于"是否值得变形"的判断 |
| **EmbodiedBench** [会议页](https://icml.cc/virtual/2025/oral/47252) · [arXiv](https://arxiv.org/abs/2502.09560) | ICML 2025（口头报告） | 🟢 [EmbodiedBench/EmbodiedBench](https://github.com/EmbodiedBench/EmbodiedBench) | 视觉驱动具身智能体的综合基准，覆盖高层规划与低层操作 | 语言层评测框架可参考 |

---

## 3. 机器人操作中的主动视觉

| 论文 | 会议 | 代码 | 做了什么 | 对本项目 |
|---|---|---|---|---|
| **Vision in Action** [论文](https://proceedings.mlr.press/v305/xiong25a.html) | CoRL 2025 | 🟢 [haoyu-x/vision-in-action](https://github.com/haoyu-x/vision-in-action) | 从人类示范学习"脖子"相机的主动注视，开源了完整的机器人颈部软硬件 | 真机阶段的主动相机硬件可参考 |
| **Eye, Robot** [论文](https://proceedings.mlr.press/v305/kerr25a.html) | CoRL 2025 | 🟢 [kerrj/eyerobot](https://github.com/kerrj/eyerobot) | 机械眼球的注视策略在 BC-RL 闭环中从任务奖励里自然涌现；单个主动相机胜过固定相机和腕部相机 | "注视从任务奖励中涌现"可作为学习型对照 |
| ★ **SaPaVe** [论文](https://openaccess.thecvf.com/content/CVPR2026/html/Liu_SaPaVe_Towards_Active_Perception_and_Manipulation_in_Vision-Language-Action_Models_CVPR_2026_paper.html) | CVPR 2026 | 🟡 [项目页](https://lmzpai.github.io/SaPaVe)（未见代码） | 把相机动作与操作动作解耦，先学语义相机控制再联合训练；构建了 20 万对数据集和 ActiveManip-Bench | 相机与身体动作解耦的思路，与我们"构型动作与运动动作分开"一致；但它的相机是自由的 |
| **ActiveVLA** [会议页](https://cvpr.thecvf.com/virtual/2026/poster/36656) · [arXiv](https://arxiv.org/abs/2601.08325) | CVPR 2026 | 🟡 仓库只有项目页 | 先定位任务关键 3D 区域，再按可见性、距离与角度多样性给候选视点打分 | **视点打分公式**可直接借用到能力图谱的可见性评分 |
| **ActiveZero** [会议页](https://neurips.cc/virtual/2026/poster/151254) | NeurIPS 2026 | ⚪ | 把主动感知建模为"信息驱动的时空记忆管理"；发布 400 万条带相机动作的数据和 ActiveBench | 背景引用 |
| **HoMMI** [论文](https://www.roboticsproceedings.org/rss22/p205.pdf) | RSS 2026 | 🟢 [xxm19/hommi](https://github.com/xxm19/hommi) | 策略只输出手部和"3D 注视目标"，再由全身控制器协调手臂、躯干、头部和底盘 | **"注视目标 → 全身运动"** 是"身体服务感知"的一种实现；但身体结构不变 |
| **ActLoc** [论文](https://proceedings.mlr.press/v305/li25b.html) | CoRL 2025 | ⚪ | 移动中主动选择视点以提高定位精度 | 背景引用 |

---

## 4. 能力感知的大模型与具身智能体

| 论文 | 会议 | 代码 | 做了什么 | 对本项目 |
|---|---|---|---|---|
| ★ **PhysVLM** [论文](https://openaccess.thecvf.com/content/CVPR2025/html/Zhou_PhysVLM_Enabling_Visual_Language_Models_to_Understand_Robotic_Physical_Reachability_CVPR_2025_paper.html) · [arXiv](https://arxiv.org/abs/2503.08481) | CVPR 2025 | 🟢 [unira-zwj/PhysVLM](https://github.com/unira-zwj/PhysVLM) | 用正运动学算出机器人可达空间，投影到深度图上把不可达区域标灰，作为单独分支输入 VLM | **最值得借鉴**：把"每个构型能看到/到达哪里"做成图像遮罩输入语言层，比文字描述更直接 |
| **EMOS** [arXiv](https://arxiv.org/abs/2410.22662) | ICLR 2025 | 🟢 [SgtVincent/EMOS](https://github.com/SgtVincent/EMOS) | 大模型读取"机器人简历"来理解各机器人能力并分配任务 | 构型简历的来源（已在计划中） |
| **COHERENT** [arXiv](https://arxiv.org/abs/2409.15146) | ICRA 2025（待核） | 🟢 [MrKeee/COHERENT](https://github.com/MrKeee/COHERENT) | 大模型协调无人机、机器狗、机械臂完成长时任务 | 异构能力推理的对照 |
| **EvoAgent** [项目页](https://feliciaxyao.github.io/EvoAgent) | ACM MM 2025（最佳学生论文） | 🟡 标注"即将发布" | 仿左右脑分工：多模态大模型负责理解，世界模型负责空间动态预测 | 关系较弱，仅作为 MM 方向的代表 |

---

## 5. 形态协同设计（ICLR / ICML / NeurIPS 主线）

| 论文 | 会议 | 代码 | 做了什么 | 对本项目 |
|---|---|---|---|---|
| ★ **Learning to Reconfigure** [会议页](https://icml.cc/virtual/2026/poster/61720) | ICML 2026 | 🟢 [Xiaoyu-Xiong/Learning-to-Reconfig](https://github.com/Xiaoyu-Xiong/Learning-to-Reconfig) | 固定骨架加关节锁定，构成可重构机器人；协同设计构型库与调度器以跨越异质地形 | **仿真基础设施来源**；它的调度器不看视觉 |
| **ECo-MoE** [会议页](https://icml.cc/virtual/2026/poster/62776) · [arXiv](https://arxiv.org/abs/2605.24225) | ICML 2026 | 🟢 [phenoweave/eco-moe](https://github.com/phenoweave/eco-moe) | 以身体编码为门控的专家混合控制器，不同身体激活不同专家，提高形态演化效率 | 若需要一个控制器覆盖所有构型，这是现成方案 |
| **形态预训练加速协同设计** [会议页](https://iclr.cc/virtual/2026/poster/10009047) · [arXiv](https://arxiv.org/abs/2502.10862) | ICLR 2026 | 🟢 [lstrgar/codesign-mpt](https://github.com/lstrgar/codesign-mpt) | 先在大量身体上预训练通用控制器，新身体无需重训即可评估（"零样本演化"）；指出共享控制器会导致设计多样性坍缩 | 构型库评估时可"零样本"估计每个构型的运动能力 |
| **House of Dextra** [会议页](https://iclr.cc/virtual/2026/poster/10007820) · [arXiv](https://arxiv.org/abs/2512.03743) | ICLR 2026 | 🟢 [An-Axolotl/House_Of_Dextra_CoDesign](https://github.com/An-Axolotl/House_Of_Dextra_CoDesign) | 灵巧手的形态与控制协同设计，一天内完成设计、训练、制造与部署 | 软硬件闭环流程参考 |
| **Stackelberg PPO** [会议页](https://iclr.cc/virtual/2026/poster/10007068) · [arXiv](https://arxiv.org/abs/2603.15388) | ICLR 2026 | ⚪ | 把形态（领导者）与控制（跟随者）建模为 Stackelberg 博弈 | 形式化参考 |
| **LOKI**（Convergent Functions, Divergent Forms）[会议页](https://neurips.cc/virtual/2025/poster/119410) · [arXiv](https://arxiv.org/abs/2505.21665) | NeurIPS 2025 | 🟢 [yeonsumia/loki](https://github.com/yeonsumia/loki) | 在隐空间中按结构相似性聚类，共享控制器，用局部搜索探索约 310 万种设计 | 大规模构型空间搜索可参考 |
| **MorphoGen** [会议页](https://neurips.cc/virtual/2026/poster/150325) | NeurIPS 2026 | 🟡 [匿名仓库](https://anonymous.4open.science/r/MorphoGen-ACC) | 大模型直接编辑定义身体的 MJCF/XML 文件来演化形态 | 用大模型生成候选构型的参考 |
| **BodyGen** [论文](https://proceedings.iclr.cc/paper_files/paper/2025/hash/66dab70dc633f6d58bada2d4e49aa58d-Abstract-Conference.html) | ICLR 2025 | 🟢 [GenesisOrigin/BodyGen](https://github.com/GenesisOrigin/BodyGen) | 高效的具身协同设计，Learning to Reconfigure 的代码基础 | 已在计划中 |
| **LASeR** [会议页](https://iclr.cc/virtual/2025/poster/30803) | ICLR 2025 | 🟢 [WoodySJR/LASeR](https://github.com/WoodySJR/LASeR) | 以大模型为进化算子设计体素软体机器人，并加入多样性反思 | 背景引用 |
| **自由形态内骨骼机器人** [会议页](https://iclr.cc/virtual/2025/poster/29135) · [arXiv](https://arxiv.org/abs/2412.01036) | ICLR 2025 | 🟡 项目页 endoskeletal.github.io | 软组织包裹刚性骨骼的机器人，进行身体与控制的联合优化 | 背景引用 |
| **Text2Robot** [arXiv](https://arxiv.org/abs/2406.19963) | ICRA 2025（据新闻稿，待核） | 🟢 [generalroboticslab/Text2Robot](https://github.com/generalroboticslab/Text2Robot) | 从文字描述生成可制造的四足机器人 | 背景引用 |

---

## 6. 可重构 / 模块化机器人

| 论文 | 会议 | 代码 | 做了什么 | 对本项目 |
|---|---|---|---|---|
| **MODUR** [arXiv](https://arxiv.org/abs/2510.13356) | IROS 2025（依据 DOI） | ⚪ | 模块化"双重可重构"机器人：既能重排模块，也能改变单个模块的形状 | 硬件参考 |
| **可重构模块腿** [arXiv](https://arxiv.org/abs/2505.00784) | PNAS（期刊，非会议） | 🟢 [Chenaah/modularlegs](https://github.com/Chenaah/modularlegs) | 单关节模块腿可拼装成多种腿足机器，损伤后可重组 | 已在上一份综述中 |

**说明：** 2025–2026 年会议上"可重构机器人 + 学习"的工作仍以运动控制为主，最有分量的是 ICML 2026 的 Learning to Reconfigure。没有找到把重构用于感知的会议论文。

---

## 7. 跨具身控制与导航

| 论文 | 会议 | 代码 | 做了什么 | 对本项目 |
|---|---|---|---|---|
| ★ **VLN-PE** [论文](https://openaccess.thecvf.com/content/ICCV2025/html/Wang_Rethinking_the_Embodied_Gap_in_Vision-and-Language_Navigation_A_Holistic_Study_ICCV_2025_paper.html) | ICCV 2025 | 🟢 [InternRobotics/InternNav](https://github.com/InternRobotics/InternNav) | 在人形、四足、轮式机器人上做物理真实的语言导航评测；性能明显下降，原因包括"受限的观测空间"、碰撞与摔倒 | **实证支持我们的动机**：身体决定观测空间；平台也可作为评测环境 |
| **Embodiment Scaling Laws** [论文](https://proceedings.mlr.press/v305/ai25a.html) | CoRL 2025 | 🟢 [BoAi01/Embodiment-Scaling-Laws](https://github.com/BoAi01/Embodiment-Scaling-Laws) | 程序化生成约 1000 种具身，发现增加具身数量比增加单具身数据泛化更好 | 构型参数化方式可借鉴 |
| **LocoFormer** [论文](https://mlanthology.org/corl/2025/liu2025corl-locoformer) · [arXiv](https://arxiv.org/abs/2509.23745) | CoRL 2025 | ⚪（PyPI 上的同名包疑为第三方复现） | 通过长上下文在线适应实现通用运动控制 | 背景引用 |
| **X-VLA** [会议页](https://iclr.cc/virtual/2026/poster/10007740) | ICLR 2026 | 🟢 [2toinf/X-VLA](https://github.com/2toinf/X-VLA) | 用软提示吸收具身差异的跨具身 VLA | 已在计划中 |
| **NavFoM** [论文](https://proceedings.iclr.cc/paper_files/paper/2026/hash/ceb45c48e29e7f49b0b47edb98e43691-Abstract-Conference.html) | ICLR 2026 | ⚪ | 跨四足、无人机、车、人形的导航基础模型 | 对立面引用 |
| **UniAct** [论文](https://openaccess.thecvf.com/content/CVPR2025/html/Zheng_Universal_Actions_for_Enhanced_Embodied_Foundation_Models_CVPR_2025_paper.html) | CVPR 2025 | 🟢 [2toinf/UniAct](https://github.com/2toinf/UniAct) | 为不同具身学习统一的"通用动作"空间 | 背景引用 |
| **NaVILA** [论文](https://roboticsproceedings.org/rss21/p018.html) | RSS 2025 | 🟢 [AnjieCheng/NaVILA](https://github.com/AnjieCheng/NaVILA) | VLA 输出中层语言动作，再由强化学习的腿足控制器执行 | 两层结构可借鉴：语言层选构型，底层控制执行 |
| **Uni-NaVid** | RSS 2025（待核） | 🟢 [jzhzhang/Uni-NaVid](https://github.com/jzhzhang/Uni-NaVid) | 统一多种导航任务的视频 VLA | 背景引用 |
| **RoVi-Aug** [论文](https://proceedings.mlr.press/v270/chen25a.html) | CoRL 2024 | 🟢 [BerkeleyAutomation/rovi-aug](https://github.com/BerkeleyAutomation/rovi-aug) | 通过机器人外观与相机视角增强实现跨具身迁移 | 同样把视角差异当干扰来消除 |

---

## 8. ICRA / IROS 补充

两个会议上的相关工作主要是 NBV 规划和可重构硬件，不涉及"形态—感知"决策。代表如下：
- **ICRA 2026：** 面向 3DGS 的目标感知 NBV（[arXiv 2602.08266](https://arxiv.org/abs/2602.08266)），代码 ⚪。
- **IROS 2025：** MODUR（见第 6 节）。
- **ICRA 2025：** COHERENT 与 Text2Robot（会议信息待核，见第 4、5 节）。

---

## 9. 尚未录用、但必须关注的 2026 预印本

| 论文 | 代码 | 做了什么 | 为什么要关注 |
|---|---|---|---|
| ★ **TVRBench**（Where to Look）[arXiv 2606.01247](https://arxiv.org/abs/2606.01247) | 🟢 [aim-uofa/TVRBench](https://github.com/aim-uofa/TVRBench) | 让智能体移动到与目标图一致的视点；最好的闭源模型成功率只有 12%；**需要移动身体时比只需转头难得多**；视觉—动作 SFT 加多轮强化学习后提升到约 51% | 最直接的证据：模型在"身体层面"的空间决策最弱 |
| ★ **LEAP** [arXiv 2609.17628](https://arxiv.org/abs/2609.17628) | ⚪ | 四足导航策略同时控制身体运动和云台深度相机，主动注视从任务奖励中涌现 | 明确说明身体俯仰/横滚**不**用于感知，正好留出了我们的空间 |
| **E3VS-Bench** [arXiv 2604.17969](https://arxiv.org/abs/2604.17969) | 🟢 [k0uya/e3vs-bench](https://github.com/k0uya/e3vs-bench) | 3DGS 场景中依赖视点的主动感知基准 | 题型可参考 |
| **CoV**（Chain-of-View）[arXiv 2601.05172](https://arxiv.org/abs/2601.05172) | 🟢 [ziplab/CoV](https://github.com/ziplab/CoV) | 免训练，让 VLM 交替推理与离散相机动作；在 OpenEQA 上平均提升约 11.6% | 免训练的语言层基线，最容易复现 |
| **ActiveArena** [arXiv 2609.24124](https://arxiv.org/abs/2609.24124) | 🟢 [leeibo/ActiveArena](https://github.com/leeibo/ActiveArena) | 35 个需要主动获取并记住证据的操作任务 | 基准参考 |
| **TAVIS** [arXiv 2605.07943](https://arxiv.org/abs/2605.07943) | 🟢 [spiglerg/tavis](https://github.com/spiglerg/tavis) | 人形躯干的主动视觉模仿学习基准；主动视觉并非处处有益 | "主动未必更好"支持我们的"有时不该变形" |
| **ParallelWorld** [arXiv 2608.22971](https://arxiv.org/abs/2608.22971) | 🟢 [AgenticEI/ParallelWorld](https://github.com/AgenticEI/ParallelWorld) | 测试时想象多条动作分支，由验证器打分后只执行最优分支的第一步 | 规划器可借鉴"想象—验证"结构 |
| **VA-Bench** [arXiv 2609.19554](https://arxiv.org/abs/2609.19554) | ⚪ | 大模型自选相机视角并给出度量控制指令；主动相机优于预设视角 | 背景引用 |
| **Active Embodiment Identification** [arXiv 2605.08020](https://arxiv.org/abs/2605.08020) | ⚪ | 腿足机器人通过主动动作辨识自身物理参数 | 自我建模的新进展 |
| **Shape Your Body** [arXiv 2606.00702](https://arxiv.org/abs/2606.00702) | ⚪ | 冻结多具身价值函数，把它当可微替代模型，对设计参数做梯度优化 | 若把价值换成"感知价值"，就可能逼近我们的问题，需要关注 |
| **GVNav** [arXiv 2502.19024](https://arxiv.org/abs/2502.19024) | ⚪ | 四足机器人视点低，与为人类视角写的导航指令不匹配，造成泛化差距 | 直接说明"相机高度由身体决定"会影响任务 |
| **EyeVLA** [arXiv 2511.15279](https://arxiv.org/abs/2511.15279) | ⚪ | VLM 输出云台与变焦指令 | 已在上一份综述中提及 |

---

## 10. 对本项目各阶段的直接用途

| 计划阶段 | 可借鉴的工作 | 怎么用 |
|---|---|---|
| S1 能力图谱 | PhysVLM、ActiveVLA | 采用 PhysVLM 的"可达空间投影成遮罩"；采用 ActiveVLA 的"可见性 + 距离 + 角度多样性"视点评分 |
| S2 构型简历 | EMOS、形态预训练（codesign-mpt）、ECo-MoE | 简历格式沿用 EMOS；运动能力可用预训练通用控制器做零样本估计 |
| S3 任务挖掘 | TVRBench、E3VS-Bench、EXPRESS-Bench、VLN-PE | 参考题型和"探索—答案一致性"指标；VLN-PE 可作为跨身体的外部验证环境 |
| S4 基线 | Active-o3、I-Perceive（自由相机）、CoV（免训练）、3D-Mem / MTU3D / Prune-Then-Plan（固定身体）、MindJourney（只想象不变形） | 组成从"不动"到"自由相机"再到"只想象"的完整对照 |
| S5 决策器 | Sea2、Prune-Then-Plan、ParallelWorld | 用感知置信度变化作为证据收益；用逐步校准决定是否值得变形 |
| 机理论文 | Theory of Space、PhysVLM-AVR、TVRBench | 借鉴信念探测的实验设计；引用"察觉 ≠ 行动"的发现作为动机 |
| 真机 | Vision in Action、Eye Robot、HoMMI | 主动相机硬件与全身注视控制 |

---

## 11. 竞争风险

- **最可能撞车的方向：**
  - 有人把 SaPaVe、ActiveZero、HoMMI 这类"主动相机 + 操作"框架推广到全身姿态，甚至可重构身体。
  - 有人把 Shape Your Body 的"价值函数作为设计替代模型"换成感知价值。
- **我们的护城河要写清楚，有三点：**
  1. 能力耦合：变形后某些动作不可达；
  2. 实测的变形代价；
  3. 会判断"不该变形"。

  目前所有工作都至少缺其中两点。
- **建议在论文中把 TVRBench 和 PhysVLM-AVR 的发现作为动机直接引用**，这比只引用经典主动感知理论更有说服力。

---

## 核实说明

- 会议信息均来自会议官网页面、CVF / PMLR / RSS 论文集，或论文首页的录用声明。以下几条是例外，需投稿前再核：
  - COHERENT 与 Text2Robot 的 ICRA 2025：后者来自新闻稿；
  - Uni-NaVid 的 RSS 2025：沿用此前记录；
  - MODUR 的 IROS 2025：依据 DOI 推断；
  - Prune-Then-Plan 的 CVPR 2026 Findings：依据论文集 URL 推断。
- 🟢 仓库都用 git ls-remote 确认可拉取。其中 ActiveVLA 的仓库只含项目页，因此标为 🟡；PhysVLM-AVR 的代码未确认是否在 PhysVLM 仓库中。
- 第 9 节都是预印本，没有录用信息，引用时请标为 arXiv。
- IJCAI 2025–2026 没有找到直接相关的工作；AAAI 和 ACM MM 各只找到 1 篇。这可能是检索覆盖不全，并不代表一定没有。
