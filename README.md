# dshell

> 🚀 基于 **DeepSeek 大模型** 的 AI Shell 工具
> **自然语言 → 自动执行 Linux 命令 → 实时输出 → 结果分析总结**

这是一个面向 **运维 / SRE / 高级用户** 的 AI CLI 工具，目标不是“帮你写命令”，而是 **真正帮你执行和分析命令**。

---

## ✨ 特性

* ✅ 使用 **DeepSeek 大模型**（非 OpenAI 依赖）
* ✅ 自然语言直接触发 **命令自动执行**
* ✅ **流式输出**

  * 命令生成过程实时可见
  * 命令执行 stdout / stderr 实时打印
  * 分析总结实时输出
* ✅ 基于 **真实执行结果** 进行分析（不臆测）
* ✅ 内置最小安全闸（可自行移除）
* ✅ 代码结构清晰，可升级为 MCP / Dify Tool

---

## 🧠 工作流程

```text
自然语言输入
   ↓
DeepSeek（生成 bash 命令，流式）
   ↓
本地自动执行命令（stdout/stderr 实时输出）
   ↓
DeepSeek（二次分析真实执行结果，流式）
   ↓
最终运维分析结论
```

---

## 📦 项目结构

```text
dshell/
├── dshell_auto_stream.py   # 主程序（自动执行 + 流式输出）
├── system_prompt.txt       # 运维安全 Prompt
└── README.md
```

---

## ⚙️ 环境要求

* Python >= 3.9
* Linux / macOS
* DeepSeek API Key
* 非 root 用户（强烈建议）

---

## 🔑 配置环境变量

```bash
export DEEPSEEK_API_KEY="sk-xxxxxxxx"
export DEEPSEEK_MODEL="deepseek-chat"        # 可选
export DSHELL_SYSTEM_PROMPT="$PWD/system_prompt.txt"
```

---

## 📥 安装依赖

```bash
pip install requests
```

---

## ▶️ 使用方式

### 直接运行

```bash
python dshell_auto_stream.py "找出当前 CPU 使用率最高的 5 个进程"
```

### 建议方式（别名）

```bash
chmod +x dshell_auto_stream.py
sudo ln -s $(pwd)/dshell_auto_stream.py /usr/local/bin/dshell
```

之后：

```bash
dshell "查看磁盘使用率最高的目录"
```

---

## 🖥️ 使用示例

```bash
dshell "统计 nginx error.log 最近 30 分钟的 502 错误数量"
```

终端输出示例：

```text
▶ 正在生成命令…
awk '$0 >= systime()-1800' /var/log/nginx/error.log | grep 502 | wc -l

▶ 正在执行命令…
42

▶ 正在分析执行结果…
- 关键发现：最近 30 分钟内出现 42 次 502 错误
- 是否异常：是
- 可能原因：后端服务响应异常或连接超时
- 运维建议：检查 upstream 服务状态和错误日志
```

---

## 🔐 安全说明（非常重要）

本工具 **会自动执行 AI 生成的命令**，请务必理解以下风险：

### 内置的最小安全限制

* 默认阻止以下高危关键词：

  * `rm -rf`
  * `mkfs`
  * `dd`
  * `shutdown`
  * `reboot`
* 单条命令执行
* 默认非 root

⚠️ **如果你删除这些限制，相当于给 AI 一个真实运维账号**

---

## 🧩 system_prompt 设计说明

`system_prompt.txt` 明确告诉模型：

* 命令会被 **直接执行**
* 禁止破坏性操作
* 默认只读、排障类命令
* 输出必须是 **可直接执行的 bash 命令**

这是本工具 **安全性的核心**

---

## 🚫 不适用场景

不建议将本工具用于：

* 生产集群自动化运行
* CI/CD 无人值守执行
* root 权限环境
* 多人共享执行节点

---

## 🧭 适用场景

* 个人运维 / SRE
* 跳板机 / 堡垒机
* 故障排查
* 日志分析
* 系统状态快速诊断

---

## 🔄 可扩展方向

本工具天然适合升级为：

* Linux MCP Server（流式）
* Dify Agent Tool
* 命令风险评分系统
* 运维审计系统
* 自动化 Runbook 执行器

---

## ⚠️ 免责声明

> 本工具会在本地执行 AI 生成的命令
> 使用者需自行承担由此产生的一切风险
> 请勿在不受控或关键生产环境中使用

---

## 📌 结语

这是一个 **偏工程、偏真实运维** 的 AI Shell 工具，
不是 Demo，不是玩具。

如果你已经看到这里，说明你知道自己在做什么 😄

---

如果你愿意，下一步我可以帮你：

* 写 **CHANGELOG**
* 加 **命令风险评分模块**
* 升级成 **MCP Server**
* 接入 **Dify / n8n**

直接告诉我你想往哪一步走。
