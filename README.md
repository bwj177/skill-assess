# skill-assess

Claude Code skill 质量与安全评估工具。作为 Claude Code skill 使用，让 Claude 自动对其他 skill 进行结构合规、安全风险、内容质量的全面评估。

## 背景

Claude Code skills 可以声明 `allowed-tools`、`hooks`、执行内联 shell 命令、打包任意 Python/Shell/JS 脚本——但目前没有安全检测机制。从第三方下载或自己创建的 skill，可能包含权限过度声明、危险代码执行、prompt injection 等风险。

## 工作原理

```
用户: /skill-assess ~/.claude/skills/some-skill
        │
        ▼
┌──────────────────────────┐
│ Phase 1: 静态分析 (脚本)   │  ← 确定性高，精确检测
│ Python AST 遍历            │
│ Shell 危险命令匹配         │
│ allowed-tools 权限分析     │
│ prompt injection 模式扫描  │
│ frontmatter 结构校验       │
│ 供应链验证                  │
│ 输出: structured findings  │
└──────────┬───────────────┘
           ▼
┌──────────────────────────┐
│ Phase 2: LLM 综合评审      │  ← 上下文理解，意图判断
│ Claude 读取 skill 文件     │
│ 结合脚本结果 + 自己理解     │
│ - 过滤误报 / 补充发现       │
│ - 触发可靠性分析            │
│ - 指令清晰度评估            │
│ - 资源设计审查              │
│ - 脚本必要性判断            │
│ 输出: qualitative analysis │
└──────────┬───────────────┘
           ▼
┌──────────────────────────┐
│ Phase 3: 报告生成          │
│ 9 维度 scorecard (1-5)     │
│ 非协商阻断项检查            │
│ 可粘贴修复建议 (Rewrites)  │
│ 触发分析                    │
│ 最终建议行动列表            │
└──────────────────────────┘
```

## 安装

```bash
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

### 静态分析（脚本精确检测）

| 维度 | 检测项 |
|------|--------|
| 结构合规 | frontmatter 必填字段、name 命名规范、description 长度、未知字段 |
| 安全性 | `allowed-tools: "*"`、subprocess shell=True、eval/exec、pickle、`curl\|sh`、prompt injection 模式 |
| 脚本分析 | Python AST 遍历、Shell 危险命令、JS/TS 调用模式 |
| 供应链 | .skillfish.json 来源、references 中的 HTTP URL |

### LLM 综合评审（Claude 判断）

| 维度 | 评估内容 |
|------|---------|
| 触发可靠性 | description 是否能让模型准确判断何时触发，是否过触发/漏触发 |
| 指令清晰度 | 步骤是否有序可执行，是否有停止条件和输出格式 |
| 资源设计 | references/scripts 是否必要，是否有 progressive disclosure |
| 脚本必要性 | 脚本是否有存在理由（重复性/确定性/易错），还是 LLM 可以直接做 |
| 输出质量 | 输出格式是否稳定，能否被下游消费 |

## 输出示例

```markdown
# Skill Review: excalidraw

## 判定
可发布

## 评分卡
- 触发可靠性: 4 — 触发条件清晰，但"画图"可能过触发
- Description 质量: 4 — 包含任务和触发词，缺负向排除
- 指令清晰度: 5 — 6 步有序流程，每步有明确动作
- 安全与权限: 5 — 无脚本无代码执行，零安全风险
- 脚本安全性: 5 — 无脚本
- 资源设计: 5 — 5 个 reference 文件，全部有指向
- 输出质量: 4 — 有格式但依赖用户指定路径
- 可维护性: 4 — 267 行，结构清晰
- 供应链安全: 4 — .skillfish.json 来源可信

## 非协商阻断项
无。

## 关键问题
无。

## 最终建议
直接使用，无风险。
```

## 项目结构

```
skill-assess/
├── SKILL.md                        # skill 定义 + 评估指令 + 输出模板
├── scripts/
│   ├── assess.py                   # 静态分析入口，输出 JSON
│   ├── checks/
│   │   ├── frontmatter.py          # 结构合规检查
│   │   ├── permissions.py          # allowed-tools 权限分析
│   │   ├── python_ast.py           # Python AST 安全分析
│   │   ├── shell_script.py         # Shell 危险命令检测
│   │   ├── js_ts.py                # JS/TS 脚本分析
│   │   ├── prompt_injection.py     # Prompt injection 模式检测
│   │   ├── quality.py              # 内容质量评估
│   │   └── supply_chain.py         # 供应链验证
│   └── utils/
│       └── parser.py               # SKILL.md 解析
└── references/
    └── assessment-guide.md         # 评分标准 + 判定规则 + 检查清单
```

## 设计灵感

参考了 [skill-reviewer](https://github.com/Nirvana-Jie/skill-reviewer) 的多维度 scorecard、非协商阻断项、可粘贴修复建议、触发分析等设计理念。

## 依赖

- Python 3.9+
- pyyaml

## License

MIT
