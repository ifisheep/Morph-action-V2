<!-- ppt-master-schema: design-spec/v1 -->
# MorphDream - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | MorphDream / MorphAction |
| Canvas Format | PPT 16:9 (1280×720) |
| Page Count | 24 |
| Target Audience | 机器学习与机器人方向研究者 |
| Communication Intent | 以问题直觉、相关工作、方法闭环、验证计划和风险收束一次组会或开题汇报 |
| Desired Audience Outcome | 理解身体是主动感知变量，并接受 MorphAction 的问题定义、方法和验证路径 |
| Core Message / Ask / Action | 将形态重构建模为信息采集动作，推进 9 周可行性验证 |
| Delivery Context | 约 25 分钟组会或开题汇报 |
| Artifact Afterlife | 研究项目汇报、开题讨论、后续论文计划底稿 |
| Reading Mode | balanced |
| Content Strategy | 结论先行，按问题→证据→挑战→方法→实验→计划→贡献组织，正文 22 页加备份 2 页 |
| Design Style | 浅色学术简洁，留白充足，深蓝单一强调色，原生形状承载流程、表格、时间线和曲线 |
| AI Image Acquisition Path | not applicable，★配图采用矢量示意 |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled，沿用主材料讲者备注并做轻度润色 |
| Custom Animations | disabled |
| Narration Audio | disabled |
| Created Date | 2026-11-22 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280 × 720 px |
| viewBox | `0 0 1280 720` |
| Margins | 76 px 左右，38 px 顶部 |
| Content Area | x=76–1204，y=112–684 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Visual style**: custom
- **Theme**: academic briefing with generous whitespace and native vector diagrams
- **Tone**: clear, restrained, research-oriented

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #F8FAFC | 浅色画布 |
| Secondary background | #EEF2F7 | 卡片、表格交替底色 |
| Primary | #1F4E9A | 唯一强调色、流程重点和关键结论 |
| Accent | #1F4E9A | 重点模块和结论 |
| Body text | #253143 | 正文与表格文字 |
| Secondary text | #667085 | 说明和脚注 |
| Divider | #D6DCE5 | 分隔线和边框 |
| Robot | #D8C5A7 | 机器人统一暖米色 |
| Furniture | #A8B0BA | 家具、线条和基线 |
| Apple | #D94343 | 目标物与否定标记 |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | 思源黑体 | Source Han Sans SC | Inter | Arial |
| Body | 思源黑体 | Source Han Sans SC | Inter | Arial |

- **Title stack**: Source Han Sans SC, Inter, Arial
- **Body stack**: Source Han Sans SC, Inter, Arial

### Font Size Hierarchy

| Purpose | Size |
| --- | --- |
| Body | 16 |
| Page title | 29 |
| Subtitle | 22 |
| Annotation | 13 |
| Footnote | 11 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 结论标题→证据或机制→一句话带走
- **Composition tendency**: 两栏、卡片、原生表格和横向时间线
- **Cross-page continuity**: 顶部深蓝短竖线、页脚和浅灰分隔线保持连续
- **Spacing posture**: 充足留白，正文控制在 5 条以内，表格页使用紧凑但清晰的字号

## VI. Icon Usage Specification

| Icon Path | Suitable Scenarios |
| --- | --- |
| native vector primitives | 蝴蝶、机器人、视线、箭头、时间线和状态标记 |

## VIII. Image Resource List

本项目不启用 AI 或网络图片，主材料中的 ★配图全部以可编辑矢量示意实现。

## IX. Content Outline

### Part 1: 问题与证据

#### Slide 01 - 梦蝶：为看见而物化

- **Audience move**: 从当前认知走向“身体决定观测空间，选择身体本身是感知决策。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 梦蝶：为看见而物化
- **Core message**: 身体决定观测空间，选择身体本身是感知决策。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 02 - 同一个目标，换一具身体才看得见

- **Audience move**: 从当前认知走向“用梦中视角筛选形态，再用真实观测验证。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 同一个目标，换一具身体才看得见
- **Core message**: 用梦中视角筛选形态，再用真实观测验证。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 03 - 机器人需要把变形当作感知决策

- **Audience move**: 从当前认知走向“变形抬高可获得证据的上限。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 机器人需要把变形当作感知决策
- **Core message**: 变形抬高可获得证据的上限。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 04 - 多项研究把瓶颈指向身体带来的观测限制

- **Audience move**: 从当前认知走向“多项研究显示移动或改变身体是观测瓶颈。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 多项研究把瓶颈指向身体带来的观测限制
- **Core message**: 多项研究显示移动或改变身体是观测瓶颈。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 05 - 真正的难点是判断何时换、换成什么、值不值得

- **Audience move**: 从当前认知走向“系统需要同时处理能力、代价和不变形选项。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 真正的难点是判断何时换、换成什么、值不值得
- **Core message**: 系统需要同时处理能力、代价和不变形选项。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 06 - 现有工作尚未同时满足感知驱动重构的六个条件

- **Audience move**: 从当前认知走向“现有工作没有同时覆盖六个条件。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 现有工作尚未同时满足感知驱动重构的六个条件
- **Core message**: 现有工作没有同时覆盖六个条件。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 07 - 最接近的工作仍把形态当作运动或姿态工具

- **Audience move**: 从当前认知走向“最接近工作仍以执行、运动或姿态为目标。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 最接近的工作仍把形态当作运动或姿态工具
- **Core message**: 最接近工作仍以执行、运动或姿态为目标。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 08 - 形态决定视点代价地形，重构在地形之间跳转

- **Audience move**: 从当前认知走向“形态是视点代价地形，重构是在地形间跳转。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 形态决定视点代价地形，重构在地形之间跳转
- **Core message**: 形态是视点代价地形，重构是在地形间跳转。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 09 - 三层动作共同追求最短时间获得足够证据

- **Audience move**: 从当前认知走向“三层动作以证据时间为目标函数。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 三层动作共同追求最短时间获得足够证据
- **Core message**: 三层动作以证据时间为目标函数。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。
- **Mathematical content**: \min_{\pi} \mathbb{E}[T_{evidence}+T_{think}+\lambda_F\mathbb{1}[fall]]

#### Slide 10 - 梦蝶闭环让每一步都经历提议、想象与择优

- **Audience move**: 从当前认知走向“梦蝶闭环让想象服务于动作，真实证据才写入记忆。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 梦蝶闭环让每一步都经历提议、想象与择优
- **Core message**: 梦蝶闭环让想象服务于动作，真实证据才写入记忆。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 11 - 一具模块化超集机器人覆盖五种视觉生态位

- **Audience move**: 从当前认知走向“五种形态对应互补的视觉生态位。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 一具模块化超集机器人覆盖五种视觉生态位
- **Core message**: 五种形态对应互补的视觉生态位。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 12 - 履历把能力耦合变成可即插即用的接口

- **Audience move**: 从当前认知走向“履历把新形态接入高层决策。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 履历把能力耦合变成可即插即用的接口
- **Core message**: 履历把新形态接入高层决策。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。
- **Mathematical content**: P(m) \subseteq P

#### Slide 13 - 先诊断看不到的原因，再决定是否换身体

- **Audience move**: 从当前认知走向“瓶颈诊断决定是否进入形态层。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 先诊断看不到的原因，再决定是否换身体
- **Core message**: 瓶颈诊断决定是否进入形态层。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 14 - 分层想象在变形前估计证据增益

- **Audience move**: 从当前认知走向“分层想象用保守证据增益支持选择。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 分层想象在变形前估计证据增益
- **Core message**: 分层想象用保守证据增益支持选择。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。
- **Mathematical content**: \operatorname{Gain}(m,v) \approx \sum_h p_t(h)P(visible\land identifiable\mid v,m,h)-\lambda\operatorname{Cost}(m,v)

#### Slide 15 - 自适应贪心给出决策骨架，切换代价留下理论空间

- **Audience move**: 从当前认知走向“贪心闭环有自适应次模性依据。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 自适应贪心给出决策骨架，切换代价留下理论空间
- **Core message**: 贪心闭环有自适应次模性依据。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 16 - 大模型提议语义动作，几何模块验证最终选择

- **Audience move**: 从当前认知走向“大模型提议，几何和履历验证。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 大模型提议语义动作，几何模块验证最终选择
- **Core message**: 大模型提议，几何和履历验证。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 17 - MuJoCo Warp 与 MolmoSpaces 构成可控验证平台

- **Audience move**: 从当前认知走向“仿真平台让藏匿类型与形态价值可控。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: MuJoCo Warp 与 MolmoSpaces 构成可控验证平台
- **Core message**: 仿真平台让藏匿类型与形态价值可控。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 18 - 基线覆盖身体约束、姿态调节和想象替代等解释

- **Audience move**: 从当前认知走向“基线覆盖主要替代解释与上界。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 基线覆盖身体约束、姿态调节和想象替代等解释
- **Core message**: 基线覆盖主要替代解释与上界。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 19 - 五组实验将四个科学主张映射到可检验指标

- **Audience move**: 从当前认知走向“实验计划覆盖 C1–C4，结果尚未开始。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 五组实验将四个科学主张映射到可检验指标
- **Core message**: 实验计划覆盖 C1–C4，结果尚未开始。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 20 - 九周计划在 1 月 3 日用 G3 决定是否冲刺

- **Audience move**: 从当前认知走向“G3 是是否冲刺 ICML 2027 的决策点。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 九周计划在 1 月 3 日用 G3 决定是否冲刺
- **Core message**: G3 是是否冲刺 ICML 2027 的决策点。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 21 - 每项主要风险都有对应的降级路径

- **Audience move**: 从当前认知走向“风险有明确降级方案。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 每项主要风险都有对应的降级路径
- **Core message**: 风险有明确降级方案。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 22 - 项目贡献是让机器人为了看见而改变自己

- **Audience move**: 从当前认知走向“贡献围绕为看见而改变身体。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 项目贡献是让机器人为了看见而改变自己
- **Core message**: 贡献围绕为看见而改变身体。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 23 - 人做判断题，编码智能体做实现题

- **Audience move**: 从当前认知走向“协作边界与防泄漏规则可测试。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 人做判断题，编码智能体做实现题
- **Core message**: 协作边界与防泄漏规则可测试。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

#### Slide 24 - 参考文献与工具支撑问题、方法和平台

- **Audience move**: 从当前认知走向“参考文献与工具对应相关工作、方法和平台。”
- **Relationships**: 标题统领正文，左到右或上到下的证据关系服务于结论
- **Composition**: 结论标题配两栏或卡片式原生矢量结构，强调色只承载关键关系
- **Title**: 参考文献与工具支撑问题、方法和平台
- **Core message**: 参考文献与工具对应相关工作、方法和平台。
- **Content**: 依据主材料对应页组织要点、表格、流程、时间线或预期示意，不新增事实。

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: notes/slide_01.md through notes/slide_24.md
- **Content**: 以主材料“讲者备注”为来源，覆盖每页标题和信息关系。备份页备注只解释其可见内容，不增加事实。
- **Total duration**: 约 25 分钟
- **Notes style**: conversational
- **Presentation purpose**: 组会或开题汇报
