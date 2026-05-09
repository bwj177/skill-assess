# skill-assess

Claude Code skill 质量与安全评估工具。作为 Claude Code skill 使用，让 Claude 自动对其他 skill 进行结构合规、安全风险、内容质量的全面评估。

## 背景

Claude Code skills 可以声明 `allowed-tools`、`hooks`、执行内联 shell 命令、打包任意 Python/Shell/JS 脚本——但目前没有安全检测机制。从第三方下载或自己创建的 skill，可能包含权限过度声明、危险代码执行、prompt injection 等风险。

## 工作原理

```
用户: /skill-assess ~/.claude/skills/some-skill
        │
        ▼
┌─────────────────────────┐
│  1. 静态分析脚本         │  Python AST、Shell 规则、JS 模式匹配
│     assess.py --json    │  输出结构化检查结果
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  2. Claude 读取 skill    │  SKILL.md、scripts 代码、hooks 配置
│     文件内容             │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  3. Claude 综合判断      │  过滤误报 + 补充发现 + 意图分析
│     （脚本结果 + 理解）   │  判断代码行为是否与声明功能一致
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│  4. 输出评估报告         │  评分 + 分维度汇总 + 详细发现 + 建议
└─────────────────────────┘
```

## 安装

```bash
# 直接放到 Claude Code skills 目录即可
cp -r skill-assess ~/.claude/skills/skill-assess
```

Claude Code 启动时会自动加载。

## 使用

```
/skill-assess ~/.claude/skills/skill-creator
```

或自然语言：

```
帮我评估一下 ~/.claude/skills/excalidraw 这个 skill
```

## 检测能力

| 维度 | 检测项 |
|------|--------|
| **结构合规** | frontmatter 必填字段、name 命名规范、description 长度、未知字段 |
| **安全性** | `allowed-tools: "*"` 过度授权、subprocess shell=True、eval/exec、pickle 反序列化、`curl\|sh` 远程执行、prompt injection 模式 |
| **质量** | body 长度、description 触发场景、allowed-tools 与实际使用的匹配 |
| **供应链** | .skillfish.json 来源、references 中的 HTTP URL |

## 项目结构

```
skill-assess/
├── SKILL.md                        # skill 定义（Claude 读取的指令）
├── scripts/
│   ├── assess.py                   # 统一入口，运行所有检查输出 JSON
│   ├── checks/
│   │   ├── frontmatter.py          # 结构合规检查
│   │   ├── permissions.py          # allowed-tools 权限分析
│   │   ├── python_ast.py           # Python AST 安全分析
│   │   ├── shell_script.py         # Shell 脚本危险模式检测
│   │   ├── js_ts.py                # JS/TS 脚本分析
│   │   ├── prompt_injection.py     # Prompt injection 模式检测
│   │   ├── quality.py              # 内容质量评估
│   │   └── supply_chain.py         # 供应链验证
│   └── utils/
│       └── parser.py               # SKILL.md 解析（frontmatter + body + 脚本文件）
└── references/
    └── assessment-guide.md         # 评估标准参考文档
```

## 评估流程

1. **静态分析**：`assess.py` 对 skill 目录运行规则检查（Python AST 遍历、Shell token 分析、frontmatter 校验），输出结构化 JSON
2. **文件审查**：Claude 读取 SKILL.md 和 scripts 代码，理解 skill 的声明功能
3. **综合判断**：Claude 结合脚本结果，判断代码行为是否与功能一致——过滤误报（如数据库 skill 调用 SQL CLI 是合理的），补充脚本规则覆盖不到的发现
4. **输出报告**：评分 + 分维度汇总 + 每条发现的分析和建议

## 评分标准

| 等级 | 分数 | 含义 |
|------|------|------|
| PASS | ≥90 | 可安全使用 |
| WARN | 60-89 | 需要人工审查 |
| FAIL | <60 | 不建议使用 |

扣分规则：CRITICAL -30, HIGH -20, MEDIUM -10, LOW -5, INFO -1

## 依赖

- Python 3.9+
- pyyaml

## License

MIT
