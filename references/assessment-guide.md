# Skill Assessment Guide

## 评分标准

每项 1-5 分。Never hand out a 5 without at least one concrete positive observation. Never hand out a 1 without naming the specific failure mode.

### 1. 触发可靠性 (Trigger reliability)

**5** — description 包含正向触发 + 负向排除 + 用户用语示例，skill 准确触发不误触发
**4** — 触发条件基本清晰，有个别边界 case 未覆盖
**3** — 有触发条件但缺负向排除，可能与同族 skill 冲突
**2** — 触发条件模糊（如仅一个关键词），经常误触发或漏触发
**1** — description 无法让模型判断何时使用（如 "帮助处理文件"）

### 2. Description 质量

**5** — 包含目标任务、正向触发、负向排除、用户用语模式，四要素齐全
**4** — 缺一项要素但整体仍可触发
**3** — 仅列出功能，无触发条件
**2** — 描述含混（如 "强大的 XX 助手"）
**1** — 三五个词，零触发信息

### 3. 指令清晰度 (Instruction clarity)

**5** — 有序可执行步骤，有停止条件、输出格式定义、失败处理，每步有动作动词
**4** — 大部分步骤可执行，有少量模糊点
**3** — 有流程但缺输出格式或停止条件
**2** — 纯原则性描述，模型需要猜测怎么做
**1** — 无指令或指令自相矛盾

### 4. 安全与权限 (Security & permissions)

**5** — allowed-tools 最小化，显式处理凭据/PII，有拒绝/升级规则
**4** — 权限基本合理，有小幅收紧空间
**3** — 缺少对敏感数据的显式处理
**2** — 权限过大（如不必要的 Bash）且无安全说明
**1** — `allowed-tools: "*"` 无理由，或存在已确认的安全漏洞

### 5. 脚本安全性 (Script safety)

**5** — 无脚本，或脚本行为与声明功能完全一致，无危险模式
**4** — 脚本合理，有轻微可改进项（如缺错误处理）
**3** — 脚本使用了 subprocess 等但未说明原因
**2** — 脚本包含网络访问、文件删除等但未在 SKILL.md 中声明
**1** — 脚本包含 eval()、pickle.load()、curl|sh 等高危模式且无合理理由

### 6. 资源设计 (Resource design)

**5** — references 从 SKILL.md 有"何时读取"指向，无重复，progressive disclosure 良好
**4** — 资源组织合理，有个别小问题
**3** — 存在未被引用的文件或内容重复
**2** — 资源命名含混或 SKILL.md 未指向任何资源
**1** — 大量死文件或 SKILL.md 过长（>500行）且未拆分

### 7. 输出质量 (Output quality)

**5** — 稳定命名的输出格式，有示例，可被下游消费
**4** — 输出基本一致，有小幅格式漂移
**3** — 输出格式模糊（如 "返回要点"），每次可能不同
**2** — 输出混合叙述和数据，无分隔
**1** — 每次运行发明新格式

### 8. 可维护性 (Maintainability)

**5** — SKILL.md < 500 行，结构清晰，每个文件单一职责
**4** — 略有冗长但可维护
**3** — 有死文件或职责不清的文件
**2** — SKILL.md 过长或依赖过多
**1** — 无法辨识文件用途，大量冗余

### 9. 供应链安全 (Supply chain)

**5** — 有 .skillfish.json 且来源可信，references 全部 HTTPS
**4** — 来源基本可信，有小幅不足
**3** — 无 .skillfish.json 但无明显风险
**2** — references 中有非 HTTPS 外部 URL
**1** — 来源不明且包含外部依赖引用

## 判定规则

### 非协商阻断项

以下情况直接判 **不可发布 (Not ready)**，不看其他维度：

1. **脚本检测到 CRITICAL** — `allowed-tools: "*"` 无理由、prompt injection 模式、eval()/pickle.load()/curl|sh 等高危代码
2. **frontmatter 不完整** — 缺少 name 或 description
3. **安全与权限 = 1** — 其他维度再高也不行
4. **触发可靠性 = 1** — 无法可靠判断何时触发的 skill 是根本性缺陷

### 维度规则

- **可发布 (Ready)** — 所有维度 ≥ 4，无关键问题
- **小幅修订后可发布 (Ready with minor revisions)** — 所有维度 ≥ 3，关键问题 ≤ 2 且均为一行修复
- **需修订 (Needs revision)** — 任一维度 = 2，或关键问题 ≥ 3
- **不可发布 (Not ready)** — 任一维度 = 1，或触发非协商阻断项

## 误报排除指南

以下模式在特定 skill 中是**合理**的，不应被标记为安全问题：

| 模式 | 合理场景 |
|------|---------|
| subprocess / CLI 调用 | 数据库 skill、部署 skill、构建工具 |
| SSH / kubectl | 运维、部署类 skill |
| 网络请求 | API 集成、数据获取类 skill |
| 文件读写 | 代码生成、配置管理类 skill |
| 内部 HTTP URL | 企业内部工具 |

**判断原则：** 代码行为是否与 skill 声明的功能一致？
