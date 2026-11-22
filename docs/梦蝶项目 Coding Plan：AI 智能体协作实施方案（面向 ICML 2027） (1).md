# 梦蝶项目 Coding Plan：AI 智能体协作实施方案（面向 ICML 2027）

Nov 21, 2026 · @Tom

## 0 目标、范围与成功标准

本计划把[研究计划书](https://claude.ai/artifact/FGNT4Td5AKdFDLoxy67SrB)落成可执行的工程任务，供编码智能体（Codex，以及你们使用的 GPT 6.2 Astra 等模型）在 Mac 和 A100 上协作完成。目标是产出 ICML 2027 论文需要的全部实验（E1 到 E5）。

### 0.1 必须交付（按优先级）

1. **仿真环境**：MolmoSpaces 场景、藏匿位置注入器，以及在 A100 上批量渲染深度图和语义掩码。
2. **超集机器人与 L1 身体层**：先交付三种形态（四足、蛇形、人马形）的步态、稳像和过渡，再补齐六足与潜望。
3. **形态履历**：全部字段由物理仿真自动测量，不手填。
4. **场景记忆、瓶颈诊断、第 0 和第 1 层想象评估器**。
5. **决策闭环**：结构化思维链提议器、贪心决策、仅在形态切换时做两步前瞻、自适应计算分配。
6. **基线、评测与图表**：全部基线共用同一套运行器和指标，E1 到 E5 可从配置一键复现。

### 0.2 本轮明确不做

- 模块对接与真实的拓扑重组。
- 端到端学习运动控制。
- 进化式评估器搜索、完整 TAMP。
- 真机实验。只预留硬件抽象层接口。
- 第 2 层生成式想象只作为可选消融，放在最后，有余力才做。

### 0.3 关口与验收标准

关口与研究计划书一致，这里补上可度量的阈值。阈值是计划目标，S0 结束时可由人根据实测调整。关口由完成条件触发，不设日期；进度能否赶上 ICML 2027 的截止日期，由人在每个关口对照官方日程判断。

| 关口 | 检查时机 | 验收标准 |
| --- | --- | --- |
| G1 | S0、S1 完成时 | 三种形态各在至少 50 个场景中连续行走 60 秒，跌倒率不超过 5%；单卡 A100 上 128×128 深度加分割的批量渲染吞吐不低于 1000 帧每秒 |
| G2 | S3、S4 完成时 | 在 200 个人工构造的候选排序用例上，评估器选出的第一名与真值可见性给出的第一名一致率不低于 80%；防泄漏测试全部通过 |
| G3 | S7.1（E1 初版）完成时 | E1 初版：完整系统在成功率或用时上优于强基线（固定形态加连续姿态调节），至少 8 个随机种子、每个种子至少 100 个回合，差异显著 |
| G4 | ICML 2027 摘要注册截止前 | 注册摘要；E2 到 E5 至少有初步结果 |
| 提交 | ICML 2027 论文截止前 | 全文与附录定稿提交 |

## 1 分工：人、编码智能体与机器

**基本原则**：凡是"判断题"都由人做，凡是"实现题"都交给智能体。判断题包括形态模板、阈值取舍、何时降级、提示词何时冻结、结果怎么解读；实现题包括写代码、写测试、跑实验、出报告。

### 1.1 角色

- **人（研究者）**
  - 维护任务看板，把每个阶段拆成任务卡（模板见第 9 节）。
  - 审阅所有合并请求，尤其是触及核心接口（第 4 节）的改动。
  - 在每个关口做去留决策；冻结提示词和数据划分；最终解读结果、写论文。
- **编码智能体（Codex 等）**
  - 每个智能体一次只领一张任务卡，在独立分支上工作。
  - 交付物包括代码、测试和 `reports/<任务编号>/` 下的简短报告。
  - 不改冻结文件，不碰测试集，不擅自修改核心接口（规则见第 7 节和第 9 节）。
  - 可以并行：S0 到 S4 期间，建议同时开 3 到 4 个智能体，分别负责仿真与场景、身体层、记忆与感知、评估器。

### 1.2 机器分工

| 工作 | Mac | A100 |
| --- | --- | --- |
| 写代码、单元测试、代码检查 | 主要 | 仅运行需要 GPU 的测试 |
| 单场景调试与可视化（MuJoCo 原生查看器） | 主要 | — |
| MuJoCo Warp 批量仿真与批量渲染 | 仅用 CPU 模式调试 | 主要 |
| 履历测量（大量重复试验） | — | 主要 |
| 开源视觉语言模型服务 | — | 主要 |
| 大规模评测与扩展曲线 | — | 主要 |
| 图表生成、报告整理 | 主要 | — |

MuJoCo Warp 快速仿真需要 NVIDIA GPU，但支持在 CPU 上开发和调试，所以 Mac 上可以跑通逻辑，再到 A100 上放大规模。

### 1.3 GPU 资源划分

视觉语言模型服务和批量仿真会争用显存。

- **有两张及以上 A100 时**：一张专门部署模型服务，其余做仿真和渲染。
- **只有一张时**：给模型服务设置显存上限，与仿真同时运行。提议器的输出全部缓存，同一记忆快照和同一提示词版本不重复调用模型。

### 1.4 硬件抽象层

本轮不做真机，但身体层的技能接口（第 4 节）按"仿真后端"和"真机后端"两种实现来设计，真机后端先留空壳。这样，后续接入实验设备时，上层代码不需要改动。

## 2 技术栈与环境

| 组件 | 选择 | 说明 |
| --- | --- | --- |
| 语言与包管理 | Python 3.12，uv，锁定 `uv.lock` | Mac 与 A100 使用同一份锁文件 |
| 物理仿真 | MuJoCo（CPU，调试）与 MuJoCo Warp（GPU，批量） | 两者版本必须配对，见 2.1 |
| 渲染 | MuJoCo Warp 批量渲染器，输出深度和分割；备选为 MuJoCo 原生 EGL 多进程渲染 | 由 S0 的验证结果决定 |
| 场景 | MolmoSpaces 场景与物体资产 | 自写参数化家具生成器作为备选和受控消融 |
| 形态锁定 | MuJoCo 关节等式约束，备选为高增益位置保持 | MuJoCo Warp 支持全部等式约束类型 |
| 视觉语言模型 | 开源模型，用 vLLM 部署为 OpenAI 兼容接口，开启 JSON Schema 约束输出 | 具体模型在 S0 通过小规模测评选定 |
| 学习组件 | PyTorch | 只用于训练版评估器基线，以及可选的局部强化学习 |
| 配置与记录 | Hydra 管理配置；实验记录写成 Parquet，配合 TensorBoard 或 W&B | 每次运行记录代码版本、配置和种子 |
| 代码质量 | ruff、pytest；关键接口加类型检查 | 持续集成只跑 CPU 测试 |
| 容器 | A100 上使用 CUDA 版 Docker 镜像；Mac 原生运行 | 镜像版本写入运行记录 |

### 2.1 版本对齐（S0 的第一项决策）

这里有一个需要尽早确认的冲突：

- 你们的仓库清单中记录了 MolmoSpaces 固定使用 MuJoCo 3.5；
- MuJoCo Warp 的发布版本与 MuJoCo 版本号同步，目前 PyPI 上已有 3.8 系列（[mujoco-warp 3.8.0.1](https://pypi.org/project/mujoco-warp/3.8.0.1/)）。

**建议方案**：用两个独立环境。

1. `scenes-export` 环境：使用 MolmoSpaces 自带的工具链（MuJoCo 3.5），把选中的场景导出为独立的 MJCF 文件和元数据。
2. `runtime` 环境：使用一对配套的新版 MuJoCo 和 MuJoCo Warp，加载导出的场景。

S0 的验证任务会检查导出的场景能否在运行环境中正确加载和渲染。如果不能，就退回"全部使用 MuJoCo 3.5 加原生多进程渲染"，并在报告中记录吞吐差距。

### 2.2 MuJoCo Warp 的已知限制

根据 PyPI 页面，MuJoCo Warp 不支持 PGS 和 noslip 求解器，也不支持插件类型的执行器和传感器（[功能说明](https://pypi.org/project/mujoco-warp/3.8.0.1/)）。超集机器人和场景的 MJCF 应避开这些特性。它的批量渲染器支持网格、纹理和每个相机不同的分辨率与内参。

### 2.3 视觉语言模型服务

- 在 S0 选 2 到 3 个候选开源模型，在 50 个代表性提示上比较三项指标：结构化输出合法率、平均延迟、空间推理质量（人工打分）。
- 提议器每次调用一次就输出 N 个候选，而不是采样 N 次，以节省调用。
- 所有调用都经过缓存层：键为"记忆快照哈希 + 提示词版本哈希 + 采样参数"。

## 3 仓库结构

目录按"谁能依赖谁"来划分。最重要的一条边界是：`imagination/` 不能依赖 `sim/`，它只能读取记忆快照（见第 7 节）。

```text
morphdream/
├── AGENTS.md                  # 编码智能体的工作规则（草案见第 9 节）
├── pyproject.toml, uv.lock
├── configs/                   # Hydra 配置：env/ robot/ agent/ exp/ fitted/
├── morphdream/
│   ├── core/types.py          # 全部数据契约（第 4 节），改动需人工审批
│   ├── sim/                   # 场景加载、藏匿位置注入、批量世界、渲染封装
│   │   ├── scenes/molmo_loader.py
│   │   ├── scenes/hiding_injector.py
│   │   ├── scenes/procedural_furniture.py   # 备选与受控消融
│   │   └── render.py
│   ├── robot/                 # 超集装配体 MJCF 生成、形态模板、关节锁定
│   │   ├── assembly.py
│   │   ├── morphologies/*.yaml
│   │   └── lock.py
│   ├── body/                  # L1 身体层
│   │   ├── gaits/             # cpg.py 及各形态步态
│   │   ├── gaze.py            # 注视与稳像
│   │   ├── skills.py          # move_to / look_at / scan / pause / transition_to
│   │   ├── transitions/       # 过渡关键帧
│   │   └── backends/          # sim 后端；real 后端留空壳
│   ├── resume/                # 履历 schema、自动测量、覆盖性筛选
│   ├── perception/            # 观测、噪声模型、检测器、验证器
│   ├── memory/                # 场景记忆、情景记忆
│   ├── reasoning/             # 证据需求解析、瓶颈诊断、提议器
│   │   └── prompts/{dev,frozen}/
│   ├── imagination/           # 第 0/1/2 层想象与评估器（禁止依赖 sim/）
│   ├── decision/              # 回合运行器、前瞻、计算分配
│   ├── baselines/             # 全部基线
│   ├── eval/                  # 数据划分、指标、统计、实验矩阵
│   └── viz/                   # 论文图表
├── splits/                    # 数据划分清单，写入后只读
├── scripts/                   # 验证任务、测量、批量评测入口
├── tests/                     # unit/ integration/ leakage/
└── reports/                   # 每个任务卡的自动报告
```

**依赖方向**：`core` ← 所有模块；`sim` 只被 `body`、`perception`（渲染观测）和 `eval` 使用；`imagination` 只依赖 `core`、`memory` 的只读快照和 `resume`。依赖方向用 import-linter 一类的工具在持续集成中强制检查。

## 4 核心接口与数据契约

所有模块之间只通过 `morphdream/core/types.py` 中的数据结构交互。它在 S0.1 中最先定下来，此后改动必须经人工审批。下面是草案，智能体实现时可以补字段，但不能改语义。

**约定**：内部一律用国际单位（米、秒、弧度），角度制只出现在配置文件里；世界坐标系 z 轴向上；位姿写成位置加四元数（w, x, y, z）。

### 4.1 形态与履历

```python
@dataclass(frozen=True)
class TransitionStat:
    mean_time_s: float
    std_time_s: float
    success_rate: float
    n_trials: int

@dataclass(frozen=True)
class JitterModel:            # 相机角抖动随速度变化的拟合
    coeffs: tuple[float, ...]
    stable_phase: tuple[float, float] | None   # 步态中适合取景的相位区间

@dataclass(frozen=True)
class Resume:
    morph_id: str
    camera_height_range_m: tuple[float, float]
    camera_pitch_range_rad: tuple[float, float]
    camera_yaw_range_rad: tuple[float, float]
    reachable_camera_poses: np.ndarray      # (N, 7)，机体坐标系；供想象模块采样
    min_clearance_height_m: float           # 能钻过的最低离地间隙
    min_width_m: float
    speed_mps: dict[str, float]             # 步态名 -> 平均速度
    jitter: dict[str, JitterModel]
    gaze_decoupled: bool                    # 注视能否与行走解耦
    self_occlusion_mask: np.ndarray         # 参考分辨率下的布尔掩码
    transitions: dict[str, TransitionStat]  # 目标形态 -> 过渡统计
    energy_per_s: float
    fall_rate_per_min: float
    provenance: dict[str, str]              # 代码版本、测量脚本、日期
```

### 4.2 观测、记忆与快照

```python
@dataclass
class Observation:
    t: float
    morph_id: str
    depth: np.ndarray                 # (H, W) 米
    seg: np.ndarray                   # (H, W) 实例编号
    seg_classes: dict[int, str]       # 实例编号 -> 类别
    rgb: np.ndarray | None
    K: np.ndarray                     # 相机内参
    T_world_cam: np.ndarray           # 估计的相机位姿（仿真中为真值加噪声）
    source: Literal["real_render"]    # 想象生成的观测不能构造出这个类型

class SceneMemory:
    def integrate(self, obs: Observation, verified: bool) -> None: ...
    def snapshot(self) -> "MemorySnapshot": ...   # 只读，传给想象模块

@dataclass(frozen=True)
class MemorySnapshot:
    occupancy: VoxelGrid              # 空闲 / 占据 / 未知
    semantics: SemanticGrid
    hypotheses: HypothesisSet         # p_t(h)
    objects: list[ObjectRecord]       # 已识别的家具及其可见几何
    content_hash: str                 # 用于缓存
```

### 4.3 瓶颈、候选动作与评分

```python
@dataclass
class Bottleneck:
    kind: Literal["occlusion", "fov", "scale", "angle", "quality", "reachability"]
    region: RegionRef
    remedy_viewpoints: list[Pose]
    reachable_by: dict[str, bool]     # 形态 -> 是否有补救视点可达
    details: dict

@dataclass
class ActionCandidate:
    level: Literal["view", "attention", "morph"]
    morph_id: str                     # 视点层和注意力层时等于当前形态
    viewpoint: Pose | None
    attention: AttentionOp | None     # 裁剪 / 放大 / 回看
    rationale: str                    # 思维链理由，只记录，不参与打分

@dataclass
class Score:
    gain: float
    gain_lcb: float                   # 保守估计，用于选择
    cost_s: float
    risk: float
    tier_used: int                    # 0 / 1 / 2
    details: dict

class Evaluator(Protocol):
    def score(self, mem: MemorySnapshot, cand: ActionCandidate,
              resumes: dict[str, Resume], state: RobotState) -> Score: ...
```

### 4.4 身体层技能

```python
@dataclass
class SkillResult:
    success: bool
    duration_s: float
    fell: bool
    observations: list[Observation]

class Body(Protocol):                 # 仿真后端与真机后端实现同一接口
    def transition_to(self, morph_id: str) -> SkillResult: ...
    def move_to(self, pose2d: Pose2D, speed: float) -> SkillResult: ...
    def look_at(self, target_xyz: np.ndarray, stabilize: bool = True) -> SkillResult: ...
    def scan(self, yaw_range: tuple[float, float], pitch_range: tuple[float, float]) -> SkillResult: ...
    def pause(self, seconds: float) -> SkillResult: ...
```

### 4.5 提议器输出格式

提议器必须输出满足下面 JSON Schema 的结果，由 vLLM 的约束解码保证格式合法。

```json
{
  "evidence_needed": "string",
  "why_not_seen": ["occlusion | fov | scale | angle | quality | reachability"],
  "candidates": [
    {
      "level": "view | attention | morph",
      "morph_id": "string",
      "target_region_id": "string",
      "attention_op": "crop | zoom | revisit | null",
      "why": "string"
    }
  ]
}
```

提议器只给出区域和动作类型，具体视点由几何采样器在该区域附近生成，再交给评估器打分。

### 4.6 回合日志

每个决策步写一行 Parquet 记录，至少包括：回合编号、数据划分、场景编号、目标类别、藏匿类型、步号、当前形态、候选列表及评分、所选动作、思考耗时、仿真耗时、证据置信度、是否成功、是否跌倒、代码版本、配置哈希、提示词哈希、随机种子。

## 5 分阶段实施计划

九个阶段中，S0 到 S4 可以由多个智能体并行推进，S5 之后逐步汇合到同一个回合运行器上。每个任务都写明运行机器、交付物和验收标准，可以直接拆成任务卡。阶段之间的先后由下表的前置条件决定。

| 阶段 | 前置条件 | 可并行 |
| --- | --- | --- |
| S0 基础设施与可行性验证 | 无；S0.1 最先完成，其余任务随后并行 | S1 |
| S1 超集机器人与 L1 身体层 | S0.1 完成（仓库骨架与 `core/types.py`） | S0、S3 |
| S2 履历测量与形态库 | G1 通过 | S3、S4 |
| S3 场景记忆与感知 | S0 完成 | S1、S2、S4 |
| S4 瓶颈诊断与想象评估器 | G1 通过 | S2、S3 |
| S5 提议器与决策闭环 | G2 通过 | S6 |
| S6 基线 | G2 通过 | S5 |
| S7 实验与分析 | 冒烟测试：S5.5 的运行器就绪；E1 初版：S5、S6 完成 | S5 与 S6 的收尾、S8 |
| S8 论文支撑 | S7 开始 | S7 |

G3 是唯一的去留关口：E1 初版必须超过强基线，才继续冲刺 ICML 2027。

### S0 基础设施与可行性验证

| 编号 | 任务 | 机器 | 交付物 | 验收 |
| --- | --- | --- | --- | --- |
| S0.1 | 仓库骨架、uv 环境、持续集成、AGENTS.md、Hydra 配置、`core/types.py` 初版 | Mac | 可运行的空项目 | `make check` 通过；接口经人工审阅 |
| S0.2 | 版本对齐验证：导出 20 个 MolmoSpaces 场景，在运行环境中加载，并用 512 个并行世界渲染 128×128 深度加分割 | A100 | `reports/S0.2/`：加载失败清单、吞吐数据、版本建议 | 人据此拍板版本组合和渲染方案 |
| S0.3 | 视觉语言模型选型：部署 2 到 3 个候选，在 50 个提示上测结构化输出合法率、延迟和空间推理质量 | A100 | 选型报告与服务脚本 | 人选定模型；接口能返回合法 JSON |
| S0.4 | 藏匿位置注入器 v0：根据物体类别和几何，找出床底、沙发底、高处、遮挡物后、低层开放格等候选位置，放入目标，并用几个固定相机高度做可见性检查，标注藏匿类型 | Mac 后 A100 | 注入器与场景清单 | 每类藏匿位置至少 50 个可用场景 |

### S1 超集机器人与 L1 身体层（与 S0 并行）

| 编号 | 任务 | 机器 | 交付物 | 验收 |
| --- | --- | --- | --- | --- |
| S1.1 | 参数化装配体 MJCF 生成器（脊柱节数、腿对数、模块尺寸、头部相机） | Mac | `robot/assembly.py` 与示例模型 | 模型能在 MuJoCo 与 MuJoCo Warp 中加载 |
| S1.2 | 形态模板与关节锁定：用 YAML 描述锁定掩码、锁定角度和接触角色 | Mac | `robot/morphologies/*.yaml`、`robot/lock.py` | 锁定后关节角漂移小于 1 度 |
| S1.3 | 四足小跑、蛇形蜿蜒、人马形（四足行走加竖起上身）的 CPG 步态，用小规模参数搜索调参 | Mac 调试，A100 搜索 | `body/gaits/` | 平地连续行走 60 秒，跌倒率不超过 5% |
| S1.4 | 注视与稳像：颈部逆运动学，加上根据机身运动预测的前馈补偿 | Mac | `body/gaze.py` | 相比关闭稳像，相机角抖动降低至少一半 |
| S1.5 | 技能接口与首批过渡（四足与人马形互换、四足与蛇形互换） | Mac | `body/skills.py`、`body/transitions/` | 平地过渡成功率不低于 90% |

**G1**：三种形态在至少 50 个场景中运行，满足第 0 节的阈值。

### S2 履历测量与形态库

| 编号 | 任务 | 机器 | 交付物 | 验收 |
| --- | --- | --- | --- | --- |
| S2.1 | 履历自动测量：对 4.1 节的每个字段写测量脚本，批量重复试验 | A100 | `resume/measure.py`、`resume/resumes/*.json` | 每个字段都有来源记录；重复测量的变异系数小于 10% |
| S2.2 | 补齐六足与潜望的步态和过渡 | Mac 后 A100 | 两种新形态 | 满足 S1 的同等阈值 |
| S2.3 | 覆盖性筛选：生成"形态—藏匿类型"的效率矩阵，并做逐一去掉某形态的分析 | A100 | 覆盖矩阵与分析报告 | 每类藏匿位置至少有一种形态是明显最优的 |

### S3 场景记忆与感知

| 编号 | 任务 | 机器 | 交付物 | 验收 |
| --- | --- | --- | --- | --- |
| S3.1 | 观测噪声模型：深度噪声、分割漏检与误检 | Mac | `perception/noise.py` | 参数可配置；有单元测试 |
| S3.2 | 占据与语义体素地图，区分空闲、占据、未知三种状态 | Mac 后 A100 | `memory/scene_memory.py` | 单环境更新速度不低于 30 次每秒 |
| S3.3 | 目标假设集：家具类别到可能藏匿位置的先验，加可选的视觉语言模型先验（离线缓存） | Mac | 假设集模块 | 合成场景测试中后验更新正确 |
| S3.4 | 验证器：真值加噪声的检测置信度；预留开放词汇检测器接口 | Mac | `perception/verifier.py` | 只接受真实渲染的观测（见第 7 节） |

### S4 瓶颈诊断与想象评估器

| 编号 | 任务 | 机器 | 交付物 | 验收 |
| --- | --- | --- | --- | --- |
| S4.1 | 可见性条件计算：遮挡、视场、尺度、视角、成像质量 | Mac | `reasoning/bottleneck.py` | 合成用例单元测试 |
| S4.2 | 补救视点采样，以及基于履历的可达性检查 | Mac | 同上 | 可达性判断与物理仿真中的实际到达结果一致率不低于 90% |
| S4.3 | 第 0 层：在记忆快照中从候选相机位姿做光线投射 | A100 | `imagination/tier0_raycast.py` | 每个候选的评估在毫秒级 |
| S4.4 | 第 1 层：由家具类别和可见下沿估计未知区域的离地间隙与内部空间 | Mac | `imagination/tier1_structural.py` | 间隙估计误差中位数小于 3 厘米 |
| S4.5 | 保守打分与代价模型；低维参数只在验证集上拟合 | Mac | `imagination/evaluator.py`、`configs/fitted/` | 参数文件带哈希 |
| S4.6 | 评估器基准：200 个候选排序用例，与真值可见性比较 | A100 | 基准脚本与报告 | 即 G2 的阈值 |

**G2**：评估器基准达标，防泄漏测试全部通过。

### S5 提议器与决策闭环

| 编号 | 任务 | 机器 | 交付物 | 验收 |
| --- | --- | --- | --- | --- |
| S5.1 | 证据需求解析 | A100 | `reasoning/evidence.py` | 对开发集任务描述输出合法结构 |
| S5.2 | 结构化思维链提议器；在开发集上迭代提示词，正式评测前由人冻结 | A100 | `reasoning/proposer.py`、`prompts/frozen/` | 结构化输出合法率不低于 99%；冻结版本带哈希 |
| S5.3 | 贪心闭环、仅在形态切换时做两步前瞻、自适应计算分配 | Mac 后 A100 | `decision/` | 单元测试与 20 个回合的冒烟测试 |
| S5.4 | 思考时间记账：墙钟时间与仿真时间分开记录 | Mac | 日志字段 | 每步都有记录 |
| S5.5 | 批量回合运行器：断点续跑、确定性种子、结果缓存 | A100 | `decision/loop.py`、`scripts/run_eval.py` | 中断后重跑结果一致 |

### S6 基线（与 S5 并行）

全部基线共用 S5 的运行器和指标。

| 编号 | 基线 | 实现要点 |
| --- | --- | --- |
| S6.1 | 最佳固定形态 | 同一闭环，形态层动作被禁用 |
| S6.2 | 固定形态加连续姿态与注视调节（强基线） | 允许调节机身高度、俯仰、横滚，但不改变接触模式 |
| S6.3 | 固定升级规则 | 视点层用尽后才允许注意力层，再允许形态层 |
| S6.4 | 纯思维链智能体 | 视觉语言模型直接选动作，不经过评估器 |
| S6.5 | VLFM 式语义前沿探索 | 参考 VLFM 的前沿与价值地图逻辑，固定形态 |
| S6.6 | 理想形态选择（上界） | 用真值告诉系统应选哪种形态 |
| S6.7 | 训练版评估器 | 在 S4 的特征上训练一个小网络，作为"免训练能否追平训练"的对照 |

### S7 实验与分析

| 编号 | 实验 | 前置条件 |
| --- | --- | --- |
| S7.1 | E1 主对比初版（G3 依据） | S5、S6 完成，提示词已冻结 |
| S7.2 | E2 零样本新形态：开发全程留出一种形态，测试时只提供履历 | G3 通过 |
| S7.3 | E3 思考与身体的扩展曲线：改变候选数与前瞻深度，以及形态库规模 | G3 通过 |
| S7.4 | E4 切换何时值得：按藏匿类型、距离、切换代价分组分析 | G3 通过；复用 S7.1 的日志 |
| S7.5 | E5 消融：去掉瓶颈诊断、第 1 层、两步前瞻，违反梦醒分离；有余力时加入第 2 层 | G3 通过 |
| S7.6 | 统计与图表：中位数、四分位距、配对自助法置信区间；图表脚本化 | 与各实验同步进行 |

**G3**：E1 初版超过强基线，决定是否冲刺 ICML 2027。

### S8 论文支撑

- S7 开始后即并行写作；智能体负责把实验报告整理成表格和图。
- 按 ICML 2027 的截止日期注册摘要（G4）。
- 收尾：定稿图表、补充材料、演示视频、复现说明，按 ICML 2027 的截止日期提交。

## 6 实验矩阵与算力预算

### 6.1 数据划分

| 划分 | 规模 | 用途 | 来源约束 |
| --- | --- | --- | --- |
| 开发集 | 约 100 个场景 | 设计提示词和模块 | 与测试集不共享场景来源 |
| 验证集 | 约 100 个场景 | 只用于拟合少数低维参数 | 同上 |
| 测试集 | 约 400 个场景 | 最终评测 | 留出至少一个 MolmoSpaces 场景来源，以及部分家具类别和目标类别 |

另外，留出一种形态用于 E2：它的履历照常测量，但不参与提示词设计和参数拟合。划分按场景来源和生成参数切分，而不只是按随机种子。

### 6.2 实验矩阵与粗略预算

下表的提议器调用量按以下假设估算：每个回合平均约 15 个决策步；每步调用一次提议器，自适应计算平均再增加约 30%。这些都是开工前的粗估，冒烟测试后按实测校准。

| 实验 | 方法或变体 | 回合数 | 提议器调用 |
| --- | --- | --- | --- |
| E1 主对比 | 本方法加 7 个基线 | 8 × 8 个种子 × 500 回合 ≈ 3.2 万 | 约 50 万次 |
| E2 零样本新形态 | 本方法、理想形态选择、训练版评估器 | 3 × 8 × 500 ≈ 1.2 万 | 约 20 万次 |
| E3 扩展曲线 | 5 档计算预算 × 3 种形态库规模 | 15 × 4 × 200 ≈ 1.2 万 | 约 20 万次 |
| E4 切换条件 | 复用 E1 日志，加 3 档切换代价的补充实验 | 约 0.6 万 | 约 10 万次 |
| E5 消融 | 5 个变体 | 5 × 4 × 500 ≈ 1 万 | 约 20 万次 |
| 合计 | — | 约 7 万 | 约 120 万次 |

### 6.3 省算力的做法

- **缓存**：提议器输出按"记忆快照哈希 + 提示词哈希"缓存；第 0 层光线投射按"快照哈希 + 相机位姿"缓存。
- **先小后大**：每个实验先用 1 个种子、50 个回合做冒烟测试，确认无误再放量。
- **提前判定**：在评测脚本中加序贯检验；差异已经非常明显的对比可以提前停止，省下的预算留给 E3。
- **优先级**：算力不够时，按 E1、E2、E3、E5、E4 的顺序保证。

## 7 防泄漏与质量规则

这些规则直接决定论文结论是否可信，必须写成代码和测试，而不是只靠约定。

### 7.1 防泄漏（每条都有对应的自动测试）

1. **想象不能偷看答案**：`imagination/` 只能读取 `MemorySnapshot`，不能导入 `sim/`，也不能访问仿真器状态。持续集成用依赖检查工具强制执行；另有一个测试：把真实场景偷偷塞给评估器时，测试必须失败。
2. **梦醒分离**：`SceneMemory.integrate` 只接受 `source == "real_render"` 且 `verified=True` 的观测。测试中尝试写入想象出的观测，必须抛出异常。
3. **提示词冻结**：`prompts/frozen/` 中每个文件都记录哈希。在测试集上运行时，脚本检查当前提示词哈希与冻结哈希一致，否则拒绝运行。
4. **数据划分只读**：`splits/` 写入后只读。测试集评测需要显式开关 `ALLOW_TEST=1`，并由人批准后才能打开。
5. **参数只在验证集上拟合**：拟合结果写入 `configs/fitted/` 并带哈希；拟合脚本拒绝读取测试集。
6. **留出形态不参与开发**：E2 的留出形态不能出现在提示词示例和参数拟合数据中，由测试检查。

### 7.2 可复现

- 每次运行记录代码版本、配置哈希、提示词哈希、模型名称与版本、随机种子、容器镜像版本。
- 回合运行器支持断点续跑；同一种子、同一配置重跑，结果应当一致（模型服务端的随机性通过固定采样参数和缓存控制）。

### 7.3 统计规范

- 每个结论至少 8 个随机种子；报告中位数与四分位距，配对比较用自助法置信区间。
- 所有运行都写入日志，报告脚本自动汇总，不手工挑选结果。
- 跨任务汇总报告逐任务结果和几何平均。

### 7.4 代码质量

- 每个合并请求都附带测试，并在 Mac 上通过 `make check`（ruff 加 CPU 测试）。
- 涉及 GPU 的改动，附上在 A100 上的冒烟测试结果。
- 合并请求只修改任务卡列出的文件；需要改核心接口时先停下来报告。

## 8 风险与降级路径

每个风险都有一个明确的触发信号和降级方案，到时由人拍板，避免在一个环节上耗掉过多时间。

| 风险 | 触发信号 | 降级方案 |
| --- | --- | --- |
| MolmoSpaces 场景在运行环境中加载失败或太慢 | S0.2 报告中失败率高，或吞吐远低于目标 | 简化碰撞几何、只用通过验证的场景子集；仍不行就改用自写参数化家具生成器 |
| MuJoCo Warp 渲染达不到需求 | S0.2 吞吐不达标 | 改用 MuJoCo 原生 EGL 多进程渲染，降低分辨率 |
| 某些形态的步态不稳（人马形、潜望风险最大） | S1.3 或 S2.2 的参数搜索完成后仍达不到 G1 阈值 | 先降速、加宽支撑；仍不行就在高层实验中采用"运动学抽象执行"：按履历测得的速度和耗时移动机器人，物理仿真只用于测量履历；论文中明确说明这一点 |
| 过渡失败率高 | 某条过渡边成功率低于 80% | 增加中间形态，走过渡图上的绕行路径；或在实验中禁用这条边 |
| 视觉语言模型输出不稳定或延迟过高 | 结构化输出合法率低于 99%，或延迟拖慢评测 | 约束解码、换更小的模型、加大缓存；必要时提议器只输出动作类型，候选由几何采样器补齐 |
| 评估器不达标 | G2 一致率低于 80% | 加强第 1 层结构先验、调整保守系数；如果仍不行，训练版评估器升为主方法的一部分，论文主张相应改写 |
| 主结果不达标 | G3 未通过 | 转投截稿更晚的会议，并利用多出的时间补齐形态、加入生成式想象 |
| 智能体产出质量参差 | 合并请求反复返工 | 拆小任务卡、强化测试、限制可修改的文件范围；关键模块由人做最终实现审阅 |
| 算力不足 | S7 中按实测吞吐，剩余实验在 ICML 2027 截止前跑不完 | 按第 6.3 节的优先级取舍；E4 只做日志分析 |

## 9 AGENTS.md 草案与任务卡模板

Codex 在开始任何工作前都会读取 AGENTS.md：它会读取全局目录下的文件、仓库根目录的文件，以及子目录中的同名文件，并按这个层次叠加（[Codex 文档](https://developers.openai.com/codex/guides/agents-md)）。官方建议保持简短，只写每次都必须遵守的规则（[Codex 定制说明](https://developers.openai.com/codex/concepts/customization)）。因此下面分为根目录的通用规则和 `imagination/` 子目录的专门规则。草案用英文书写，便于各类模型稳定遵循。

### 9.1 根目录 AGENTS.md

```markdown
# AGENTS.md — MorphDream

## Project
Research code for cross-morphology active visual search with a reconfigurable
modular robot (paper target: ICML 2027). Plan: see docs/coding_plan.md.

## Setup
- Mac (CPU): `uv sync` then `make check` (ruff + pytest -m "not gpu").
- A100: use the `morphdream:cuda` image; GPU tests: `pytest -m gpu`.

## Golden rules
1. Work only on the files listed in your task card. If you need to change
   `morphdream/core/types.py`, stop and report instead.
2. Never edit `prompts/frozen/`, `splits/`, or `configs/fitted/` unless the task
   card explicitly says so.
3. Never run on the test split. Test runs require `ALLOW_TEST=1`, set by a human.
4. Every change ships with tests. Run `make check` before you finish.
5. Every experiment run logs git hash, config hash, prompt hash, model, and seed,
   and writes results to `reports/<task-id>/`.
6. Units are SI internally (m, s, rad). World frame is z-up. Poses are
   position + quaternion (w, x, y, z).

## Reporting
End every task with: what changed, test results, numbers produced,
open questions, suggested next step. Write the same into
`reports/<task-id>/README.md`.
```

### 9.2 `morphdream/imagination/AGENTS.md`

```markdown
# Rules for the imagination module
- Read only `MemorySnapshot`, `Resume`, and `core` types.
- Never import from `morphdream.sim` or touch simulator state; CI enforces this.
- Imagined observations are never passed to `SceneMemory.integrate`.
- Scores must include a conservative estimate (`gain_lcb`) for anything that
  depends on unknown space.
```

### 9.3 任务卡模板

```markdown
## Task <ID>: <title>
Stage: <S0–S8> | Machine: <Mac / A100>
Context: <why this task exists; link to plan section>
Inputs: <files, interfaces, data it may read>
Deliverables: <files to create or modify>
Acceptance criteria: <measurable checks>
Tests to add: <list>
Do not touch: <files or directories>
Report: reports/<ID>/README.md
```

### 9.4 示例任务卡

```markdown
## Task S4.3: Tier-0 ray-casting imagination
Stage: S4 | Machine: A100 (develop on Mac with CPU fallback)
Context: Plan sections 4.3 and 7.1. Scores candidate viewpoints by ray casting
  in the memory snapshot only.
Inputs: core/types.py (MemorySnapshot, ActionCandidate, Resume, Score)
Deliverables: morphdream/imagination/tier0_raycast.py,
  tests/unit/test_tier0.py, tests/leakage/test_no_sim_import.py
Acceptance criteria:
  - On 20 hand-built snapshots, visible-probability matches brute-force ray
    casting within 1e-3.
  - Median scoring time per candidate under 5 ms on A100.
  - Leakage test fails if any module in imagination/ imports morphdream.sim.
Tests to add: as listed above.
Do not touch: core/types.py, memory/, sim/.
Report: reports/S4.3/README.md
```

### 9.5 智能体协作的节奏

- 人维护看板，按第 5 节的阶段依赖派卡：某个智能体交付后，再给它分配下一张前置条件已满足的任务卡。
- 智能体完成后提交合并请求和报告；人审阅合并后，依赖它的任务卡才能开始。
- 每完成一个阶段、每次关口检查前，做一次集成：在 A100 上跑全量测试和一个端到端冒烟实验，结果写入 `reports/integration/<阶段或关口编号>/`。
- 遇到需要判断的问题（阈值、降级、接口变更），智能体停下并在报告中列出选项，由人决定。

## 10 参考开源仓库的使用方式

以下基于你们 11 月 10 日整理的仓库清单，只列出对本计划有直接用处的部分。

**许可证提醒**：清单中只确认了 Learning-to-Reconfig 和 MolmoSpaces 为 Apache-2.0。其他仓库在复制代码前，必须由智能体先核对许可证并写进任务报告；只参考思路、不复制代码的情况不受影响。

| 阶段 | 仓库 | 用法 |
| --- | --- | --- |
| S0 场景 | [allenai/molmospaces](https://github.com/allenai/molmospaces) | 场景与物体资产来源。它包含 23 万多个室内场景和 13 万多个带类别、尺度、质量等元数据的物体，场景来自 iTHOR-120、ProcTHOR-10K、ProcTHOR-Objaverse 和 Holodeck 等数据集（[Ai2 博客](https://allenai.org/blog/molmospaces)）。这让"按场景来源留出测试集"很容易实现 |
| S0、S7 仿真 | [google-deepmind/mujoco\_warp](https://github.com/google-deepmind/mujoco_warp)、[mujoco\_playground](https://github.com/google-deepmind/mujoco_playground) | 批量仿真与渲染；步态调不好时，参考 Playground 的足式运动训练流程 |
| S1 装配体 | [Chenaah/Metamachine](https://github.com/Chenaah/Metamachine)、[Chenaah/modularlegs](https://github.com/Chenaah/modularlegs) | 参考它们由构型编码生成 MJCF 的方式；CPG 不够用时，参考 modularlegs 的单构型运动训练脚本 |
| S1 锁定 | [Xiaoyu-Xiong/Learning-to-Reconfig](https://github.com/Xiaoyu-Xiong/Learning-to-Reconfig) | 锁定控制器可以移植（Apache-2.0）；它的调度器只看本体状态、为通过性而重构，适合在相关工作中作为最直接的对照 |
| S2 履历 | [SgtVincent/EMOS](https://github.com/SgtVincent/EMOS) | 从 URDF 自动生成"机器人简历"的思路，可以参考字段设计，并在论文中引用 |
| S6 基线 | [bdaiinstitute/vlfm](https://github.com/bdaiinstitute/vlfm)、[Stanford-ILIAD/explore-eqa](https://github.com/Stanford-ILIAD/explore-eqa)、[UMass-Embodied-AGI/3D-Mem](https://github.com/UMass-Embodied-AGI/3D-Mem) | 把它们的前沿探索和停止判据逻辑改写为固定身体的基线 |
| 相关工作 | [Ainaz99/OneRING](https://github.com/Ainaz99/OneRING) | 它把身体与相机差异当作要泛化掉的变量，正好是本文的对立面。它基于 AI2-THOR，移植成本高，建议只在相关工作中讨论，不做实验基线 |
| 后续扩展 | [nico-bohlinger/one\_policy\_to\_run\_them\_all](https://github.com/nico-bohlinger/one_policy_to_run_them_all)、BodyTransformer、get\_zero | 若以后用一个共享策略统一各形态的底层控制，从这里起步 |
| 后续扩展 | BodyGen、robomorph、modularlegs 的贝叶斯优化部分 | 把"按覆盖率选形态库"升级为自动形态搜索 |
| 后续扩展 | CMRRP、VisibleSim | 模块真实拆装重组时的自重构规划 |

**不建议在本轮引入**：跨具身 VLA 一类的大模型（Qwen-VLA、X-VLA、openpi 等）。它们和本文的关系主要是"对立面"，适合写进引言和相关工作，不适合进入实现范围。
