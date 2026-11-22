# Protean Perception — 相关开源仓库清单

整理日期：2026-11-10

**核实说明**

- 所有仓库地址都确认过真实可访问。
- 标 ★ 的 13 个读过 README；其余按对应论文的内容描述。
- 星标数、维护状态和许可证没有逐个查。已确认许可证的只有 Learning-to-Reconfig 和 MolmoSpaces，均为 Apache-2.0。

---

## 0. 建议先看的五个

| 仓库 | 是什么 | 对本项目的用处 |
|---|---|---|
| ★ [Chenaah/Metamachine](https://github.com/Chenaah/Metamachine) | MuJoCo 上的模块化机器人仿真框架，可 `pip install metamachine`。目前实现的是"模块化腿"：单自由度模块可自由拼成米级足式机器人 | 和我们的技术栈最接近（MuJoCo + 模块化）。参考它如何由构型编码生成 MJCF，用来造骨架和候选构型 |
| ★ [Chenaah/modularlegs](https://github.com/Chenaah/modularlegs) | 上面框架对应的论文代码（Agile Legged Locomotion in Reconfigurable Modular Robots）。含单模块和四足的 RL 训练脚本、真机部署、对构型做贝叶斯优化 | 各构型的运动 primitive 怎么训练；构型搜索怎么做 |
| ★ [Xiaoyu-Xiong/Learning-to-Reconfig](https://github.com/Xiaoyu-Xiong/Learning-to-Reconfig) | ICML 2026。固定骨架，用关节锁定定义构型，上层调度器决定何时切换。Apache-2.0，MuJoCo 2.3.3 + SB3 PPO | 锁定控制器（`opt/utils/reconfig.py`）可以直接移植。它的调度器只看本体状态、为通过性而重构，是我们最直接的对照 |
| ★ [Ainaz99/OneRING](https://github.com/Ainaz99/OneRING) | RING 导航通才策略。在 AI2-THOR 里随机采样约 100 万种具身（身体尺寸、相机数量、相机参数与安装位置）训练 | 它把身体和相机差异当作要"泛化掉"的变量，正好是我们的对立面。具身参数化方式可对照我们的"能力点"，也可当学习型基线 |
| ★ [nico-bohlinger/one_policy_to_run_them_all](https://github.com/nico-bohlinger/one_policy_to_run_them_all) | URMA，CoRL 2024。一个策略控制多种足式机器人，基于 RL-X | 以后若想用"一个策略管所有构型"替代"每个构型一个 primitive"，这是起点（纪要里的创新 B） |

---

## 1. 模块化与可重构机器人

| 仓库 | 说明 | 备注 |
|---|---|---|
| ★ [Chenaah/Metamachine](https://github.com/Chenaah/Metamachine) | 模块化机器人仿真框架 | MuJoCo；仍在早期开发 |
| ★ [Chenaah/modularlegs](https://github.com/Chenaah/modularlegs) | 可重构模块化足式机器人的运动学习 | 正逐步迁移到 Metamachine |
| ★ [Xiaoyu-Xiong/Learning-to-Reconfig](https://github.com/Xiaoyu-Xiong/Learning-to-Reconfig) | 关节锁定构型 + 调度器 | 基于 BodyGen 改写 |
| ★ [biorobotics/learning_modular_policies](https://github.com/biorobotics/learning_modular_policies) | CMU，基于模型的 RL 训练模块化策略，含真机 | PyBullet，不是 MuJoCo |
| ★ [JanusMaple/CMRRP](https://github.com/JanusMaple/CMRRP) | 连续体模块化机器人的自重构规划（Atlas-RRT* 做运动规划，MCTS 做任务规划） | 面向模块真实拆装重组 |
| [VisibleSim/VisibleSim](https://github.com/VisibleSim/VisibleSim) | 晶格型模块化机器人的行为仿真器 | 偏分布式自重构算法 |
| [SgtVincent/EMOS](https://github.com/SgtVincent/EMOS) | ICLR 2025。从 URDF 自动生成"机器人简历"，Habitat 上的异构多机器人基准 | 我们的 Resume 概念由此扩展 |

CMRRP 和 VisibleSim 面向"模块之间真的拆装重组"，本文不做，留作后续参考。

---

## 2. 跨形态控制（RL）

| 仓库 | 说明 | 备注 |
|---|---|---|
| ★ [nico-bohlinger/one_policy_to_run_them_all](https://github.com/nico-bohlinger/one_policy_to_run_them_all) | URMA：一个策略控制多种足式机器人 | 依赖 [nico-bohlinger/RL-X](https://github.com/nico-bohlinger/RL-X) |
| [carlosferrazza/BodyTransformer](https://github.com/carlosferrazza/BodyTransformer) | 把身体结构作为注意力掩码的策略网络 | |
| ★ [real-stanford/get_zero](https://github.com/real-stanford/get_zero) | 图具身 Transformer，硬件改动后零样本适应 | 实验对象是 LEAP 手；Isaac Gym |
| ★ [amathislab/dmap](https://github.com/amathislab/dmap) | 身体参数变化时仍能行走的分布式注意力策略，NeurIPS 2022 | PyBullet |
| [agrimgupta92/metamorph](https://github.com/agrimgupta92/metamorph) | MetaMorph：Transformer 通用形态控制 | 经典一脉 |
| [MasterXiong/ModuMorph](https://github.com/MasterXiong/ModuMorph) | MetaMorph 的后续改进 | 经典一脉 |
| [yobibyte/amorpheus](https://github.com/yobibyte/amorpheus) | Amorpheus：用注意力替代图结构消息传递 | 经典一脉 |
| [huangwl18/modular-rl](https://github.com/huangwl18/modular-rl) | 共享模块化策略（SMP） | 经典一脉 |
| [BoAi01/Embodiment-Scaling-Laws](https://github.com/BoAi01/Embodiment-Scaling-Laws) | 仓库名对应"具身数量的规模律"那篇论文 | 只确认了仓库存在，没读内容 |

---

## 3. 跨具身 VLA / VLN

| 仓库 | 说明 |
|---|---|
| ★ [QwenLM/Qwen-VLA](https://github.com/QwenLM/Qwen-VLA) | 用文本提示指定具身，一套权重覆盖操作和导航 |
| [2toinf/X-VLA](https://github.com/2toinf/X-VLA) | ICLR 2026，每种具身一组软提示 |
| [rail-berkeley/crossformer](https://github.com/rail-berkeley/crossformer) | 统一 token 序列的跨具身策略 |
| [liruiw/HPT](https://github.com/liruiw/HPT) | 具身专属的输入干 + 共享主干 |
| [OpenDriveLab/UniVLA](https://github.com/OpenDriveLab/UniVLA) | RSS 2025，以任务为中心的潜在动作 |
| [NVIDIA/Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) | 主流开源 VLA |
| [Physical-Intelligence/openpi](https://github.com/Physical-Intelligence/openpi) | 主流开源 VLA |
| [octo-models/octo](https://github.com/octo-models/octo) | 主流开源 VLA |
| [openvla/openvla](https://github.com/openvla/openvla) | 主流开源 VLA |
| ★ [Ainaz99/OneRING](https://github.com/Ainaz99/OneRING) | 随机具身训练的室内导航通才策略 |
| [robodhruv/visualnav-transformer](https://github.com/robodhruv/visualnav-transformer) | GNM / ViNT / NoMaD，跨机器人视觉导航 |
| [AnjieCheng/NaVILA](https://github.com/AnjieCheng/NaVILA) | 足式机器人 VLN |
| [jzhzhang/Uni-NaVid](https://github.com/jzhzhang/Uni-NaVid) | 统一导航模型 |
| [allenai/spoc-robot-training](https://github.com/allenai/spoc-robot-training) | SPOC：仿真中模仿最短路径的导航与操作 |
| [allenai/poliformer](https://github.com/allenai/poliformer) | PoliFormer：大规模 RL 导航策略 |

没找到代码的：

- **NavFoM**（ICLR 2026 的跨具身导航基础模型）：项目页上没有代码链接。
- **CanonNav**（arXiv 2608.30242）和 **Sensor-Layout-Agnostic Navigation**（arXiv 2610.08306）：只找到论文。两者都在做"把相机几何差异消掉"，可作为相关工作引用。

这一类对本文的价值主要在"对立面"：它们都把具身当作需要适配的给定条件，没有一个把"换身体"当作动作。适合放在引言和相关工作里。

---

## 4. 形态设计与搜索

| 仓库 | 说明 | 备注 |
|---|---|---|
| ★ [GenesisOrigin/BodyGen](https://github.com/GenesisOrigin/BodyGen) | ICLR 2025 Spotlight，形态与控制协同设计 | LTR 的基座；依赖老的 mujoco-py。旧地址 Josh00-Lu/BodyGen 仍可访问 |
| [Khrylx/Transform2Act](https://github.com/Khrylx/Transform2Act) | 把"改形态"作为策略动作的开山之作 | |
| [allanzhao/RoboGrammar](https://github.com/allanzhao/RoboGrammar) | 基于语法的机器人设计空间 | |
| [JiahengHu/GLSO](https://github.com/JiahengHu/GLSO) | 语法引导的潜空间搜索 | |
| [EvolutionGym/evogym](https://github.com/EvolutionGym/evogym) | 软体机器人形态演化基准 | |
| [Yuxing-Wang-THU/ModularEvoGym](https://github.com/Yuxing-Wang-THU/ModularEvoGym) | EvoGym 的模块化版本 | |
| [agrimgupta92/derl](https://github.com/agrimgupta92/derl) | 深度进化强化学习（Unimal） | |
| ★ [kevinxqiu/robomorph](https://github.com/kevinxqiu/robomorph) | ICRA 2026。LLM 生成设计，编译成 MuJoCo XML，Brax 训练后再进化 | |
| [generalroboticslab/Text2Robot](https://github.com/generalroboticslab/Text2Robot) | 文本生成机器人网格，再做进化优化 | |
| ★ [Yuxing-Wang-THU/SurveyBrainBody](https://github.com/Yuxing-Wang-THU/SurveyBrainBody) | 协同设计综述的论文清单 | 适合当索引 |

---

## 5. 基础设施与感知侧基线

**仿真与资产**

| 仓库 | 说明 |
|---|---|
| [allenai/molmospaces](https://github.com/allenai/molmospaces) | 23 万室内场景，MuJoCo 原生 MJCF，带物体元数据。本项目的场景来源；固定用 MuJoCo 3.5 |
| [google-deepmind/mujoco_playground](https://github.com/google-deepmind/mujoco_playground) | GPU 上分钟级训练足式运动策略 |
| [google-deepmind/mujoco_menagerie](https://github.com/google-deepmind/mujoco_menagerie) | 高质量机器人 MJCF 模型库 |
| [google-deepmind/mujoco_warp](https://github.com/google-deepmind/mujoco_warp) | MuJoCo 的 GPU 后端 |
| [robfiras/loco-mujoco](https://github.com/robfiras/loco-mujoco) | 足式与人形运动的模仿学习基准 |

**零样本探索与问答**

| 仓库 | 说明 |
|---|---|
| [Stanford-ILIAD/explore-eqa](https://github.com/Stanford-ILIAD/explore-eqa) | Explore until Confident：前沿探索 + 校准置信度决定何时停止 |
| [UMass-Embodied-AGI/3D-Mem](https://github.com/UMass-Embodied-AGI/3D-Mem) | CVPR 2025，基于记忆快照的探索与问答 |
| [SaumyaSaxena/graph_eqa](https://github.com/SaumyaSaxena/graph_eqa) | GraphEQA：三维场景图做记忆，用 Stretch 真机验证过 |
| [bdaiinstitute/vlfm](https://github.com/bdaiinstitute/vlfm) | VLFM：视觉语言前沿地图，零样本目标导航 |
| [facebookresearch/open-eqa](https://github.com/facebookresearch/open-eqa) | OpenEQA 数据与 LLM 评测协议 |

---

## 6. 对应到 coding plan 的哪一步

| 阶段 | 用哪些仓库 | 怎么用 |
|---|---|---|
| S0 场景接入 | molmospaces | 场景 MJCF 和元数据格式 |
| S2 骨架、Resume、构型库 | Metamachine、modularlegs、Learning-to-Reconfig | 构型编码到 MJCF；锁定与重构控制器 |
| S2 运动 primitive | modularlegs、mujoco_playground、one_policy_to_run_them_all | 开环步态调不好时，用它们训练各构型的速度跟踪策略 |
| S4 基线 | OneRING、explore-eqa、3D-Mem、vlfm | OneRING 作为"具身无关策略"对照；后三个的前沿探索逻辑改写成固定身体的基线 |
| S5 语言与评测 | open-eqa、graph_eqa | 评测协议与提示词参考 |
| 后续：跨构型统一控制器 | BodyTransformer、get_zero、one_policy_to_run_them_all | 纪要中的创新 B |
| 后续：构型自动设计 | BodyGen、robomorph、modularlegs（贝叶斯优化部分） | 把"按覆盖率选构型库"升级为学习式搜索 |
| 后续：模块真重组 | CMRRP、VisibleSim | 自重构规划 |

---

## 7. 相关论文与项目页

- [Learning to Reconfigure 项目页](https://ltrweb.github.io/learning_to_reconfigure/)
- [The One RING 项目页](https://allenai.github.io/one-ring/) · [arXiv 2412.14401](https://arxiv.org/abs/2412.14401)
- [NavFoM 项目页](https://pku-epic.github.io/NavFoM-Web/)
- [One Policy to Run Them All 项目页](https://nico-bohlinger.github.io/one_policy_to_run_them_all_website/)
- [GET-Zero 项目页](https://get-zero-paper.github.io/)
- [Agile legged locomotion in reconfigurable modular robots（PNAS）](https://www.pnas.org/doi/10.1073/pnas.2519129123)
- [Learning Modular Robot Control Policies（arXiv 2105.10049）](https://arxiv.org/html/2105.10049v2)
- [RoboMorph（arXiv 2407.08626）](https://arxiv.org/abs/2407.08626)
- [Embodied Co-Design 综述（arXiv 2512.04770）](https://arxiv.org/pdf/2512.04770)
- [CanonNav（arXiv 2608.30242）](https://arxiv.org/html/2608.30242)
- [Sensor-Layout-Agnostic Navigation（arXiv 2610.08306）](https://arxiv.org/abs/2610.08306)
- [Towards Embodiment Scaling Laws in Robot Locomotion（arXiv 2505.05753）](https://arxiv.org/pdf/2505.05753)
- [MolmoSpaces（arXiv 2602.11337）](https://arxiv.org/pdf/2602.11337)
- [MuJoCo Playground（arXiv 2502.08844）](https://arxiv.org/html/2502.08844v1)
