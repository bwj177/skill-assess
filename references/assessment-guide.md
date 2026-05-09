# Skill Assessment Guide

## 评估维度

### 1. 结构合规 (Structure)
- frontmatter 必须有 `name` 和 `description`
- name 必须是 kebab-case，≤64 字符
- description 不能含 `< >`，≤1024 字符

### 2. 安全性 (Security)

**高危模式：**
- `allowed-tools: "*"` — 完全绕过权限，除非功能确实需要
- `subprocess(..., shell=True)` — shell 注入风险
- `eval()` / `exec()` — 动态代码执行
- `pickle.load()` — 反序列化不可信数据
- `curl | sh` — 远程代码执行
- `rm -rf /` — 破坏性操作
- Prompt injection — 劫持模型行为

**合理例外（不是安全问题）：**
- 数据库 skill 做 SQL 查询、subprocess 调用 CLI 工具
- 部署 skill 使用 SSH、kubectl 等运维工具
- 内部 skill 访问公司内网 HTTP URL
- skill-creator 调用 `claude -p` 进行 eval 测试

**判断原则：** 代码行为是否与 skill 声明的功能一致？

### 3. 质量 (Quality)
- description 应包含触发场景描述
- body 不宜过长（建议 <500 行），详细文档放 references/
- 建议有 eval 测试和 LICENSE

### 4. 供应链 (Supply Chain)
- 建议有 .skillfish.json 记录来源
- references 中的外部 URL 应使用 HTTPS

## 评分

| 等级 | 分数 | 含义 |
|------|------|------|
| PASS | ≥90 | 可安全使用 |
| WARN | 60-89 | 需要人工审查 |
| FAIL | <60 | 不建议使用 |

## 评估报告格式

Claude 应输出：
1. 总体评分和等级
2. 分维度汇总（表格）
3. 详细发现列表（按严重性排序）
4. 综合判断和建议
