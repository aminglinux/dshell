#!/usr/bin/env python3
import os
import sys
import subprocess
import requests
import json
import threading

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
API_KEY = os.getenv("DEEPSEEK_API_KEY")

SYSTEM_PROMPT_PATH = os.getenv(
    "DSHELL_SYSTEM_PROMPT",
    os.path.expanduser("./system_prompt.txt")
)

BLOCKED_KEYWORDS = [
    "rm -rf",
    "mkfs",
    "dd ",
    "shutdown",
    "reboot",
]

def load_system_prompt():
    with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

# ===== DeepSeek 流式调用 =====
def stream_deepseek(messages, prefix=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 512,
        "stream": True,
    }

    with requests.post(
        DEEPSEEK_API_URL,
        headers=headers,
        json=payload,
        stream=True,
        timeout=60,
    ) as resp:
        resp.raise_for_status()
        full_text = ""
        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if not line.startswith("data:"):
                continue
            data = line.replace("data:", "").strip()
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
                delta = chunk["choices"][0]["delta"].get("content", "")
                if delta:
                    if prefix:
                        print(delta, end="", flush=True)
                    full_text += delta
            except Exception:
                continue
        print()
        return full_text.strip()

def is_dangerous(cmd: str) -> bool:
    return any(k in cmd for k in BLOCKED_KEYWORDS)

# ===== 命令流式执行 =====
def stream_execute(cmd: str):
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    def stream(pipe, label=None):
        for line in pipe:
            print(line, end="", flush=True)

    t_out = threading.Thread(target=stream, args=(process.stdout,))
    t_err = threading.Thread(target=stream, args=(process.stderr,))

    t_out.start()
    t_err.start()

    process.wait()
    t_out.join()
    t_err.join()

    return process.returncode

def main():
    if not API_KEY:
        print("❌ DEEPSEEK_API_KEY 未设置")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("用法: dshell-auto \"自然语言指令\"")
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])

    # ===== 1. 流式生成命令 =====
    print("\n▶ 正在生成命令…\n")
    command = stream_deepseek(
        [
            {"role": "system", "content": load_system_prompt()},
            {"role": "user", "content": user_input},
        ],
        prefix=True,
    )

    print("\n▶ 生成完成\n")

    if is_dangerous(command):
        print("❌ 命令包含高危关键词，已阻止执行")
        sys.exit(2)

    # ===== 2. 流式执行命令 =====
    print("▶ 正在执行命令…\n")
    code = stream_execute(command)
    print(f"\n▶ 执行结束，退出码: {code}\n")

    # ===== 3. 流式分析结果 =====
    print("▶ 正在分析执行结果…\n")

    analysis_prompt = f"""
以下是 Linux 命令的真实执行情况，请进行运维分析。

命令：
{command}

退出码：{code}

请输出：
- 关键发现
- 是否异常
- 可能原因
- 运维建议
"""

    stream_deepseek(
        [
            {"role": "system", "content": "你是一个资深 Linux 运维工程师，只分析真实执行结果。"},
            {"role": "user", "content": analysis_prompt},
        ],
        prefix=True,
    )

if __name__ == "__main__":
    main()
