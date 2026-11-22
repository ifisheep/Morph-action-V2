<!-- ppt-master-schema: spec-lock/v1 -->
# Execution Lock

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## communication
- primary_language: zh-CN
- audience: 机器学习与机器人方向研究者
- objective: 在约 25 分钟内说明身体是主动感知变量，并给出 MorphAction 的方法与验证计划
- core_message: 形态重构是一种信息采集动作，思考不能替代身体
- consumption_mode: balanced

## mode
- mode: custom
- mode_behavior: 结论先行，以问题直觉和证据建立张力，再通过方法闭环、实验计划和风险收束

## visual_style
- visual_style: custom
- visual_style_behavior: 浅色学术画布、深蓝单一强调色、圆角卡片、原生表格与流程图、充足留白、细灰分隔线

## colors
- bg: #F8FAFC
- secondary_bg: #EEF2F7
- primary: #1F4E9A
- accent: #1F4E9A
- text: #253143
- secondary_text: #667085
- divider: #D6DCE5
- robot: #D8C5A7
- furniture: #A8B0BA
- apple: #D94343

## typography
- font_family: Source Han Sans SC, Inter, Arial
- title_family: Source Han Sans SC, Inter, Arial
- body_family: Source Han Sans SC, Inter, Arial
- annotation_family: Source Han Sans SC, Inter, Arial
- footer_family: Inter, Source Han Sans SC, Arial
- body: 16
- title: 29
- subtitle: 22
- annotation: 13
- footnote: 11

## icons
- library: none
- inventory: native vector primitives

## page_rhythm
- P01: anchor
- P02: breathing
- P03: anchor
- P04: dense
- P05: dense
- P06: dense
- P07: dense
- P08: breathing
- P09: dense
- P10: anchor
- P11: dense
- P12: dense
- P13: dense
- P14: dense
- P15: dense
- P16: dense
- P17: dense
- P18: dense
- P19: anchor
- P20: dense
- P21: dense
- P22: anchor
- P23: breathing
- P24: breathing

## pptx_structure
- mode: flat

## forbidden
- `mask`, `<style>`, `class`, external CSS, `<foreignObject>`, `textPath`, `@font-face`, `<animate*>`, `<set>`, `<script>` / event attributes, `<iframe>`
- HTML named entities in text; write typography as raw Unicode and escape XML reserved characters
- 不要编造任何数据或实验结果 (user)
- 第 19 页的结果图必须醒目标注“预期结果（示意）” (user)
- 主材料没有的论文不要添加 (user)
- 流程图、表格、时间线、雷达图都做成可编辑的原生形状 (user)
