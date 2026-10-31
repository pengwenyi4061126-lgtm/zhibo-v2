#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""直播中控台 — 话术提词 + 评论区助手 + 问答库

只用 Python 标准库，不需要 pip install 任何东西。
启动：  python console/server.py
然后浏览器打开 http://127.0.0.1:8777
提词器（可作为 OBS 浏览器源）： http://127.0.0.1:8777/teleprompter
"""
import json
import os
import sys
import threading
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PORT = int(os.environ.get("CONSOLE_PORT", "8777"))

# 语音合成产物目录（放在工作区外，避免大文件进 git）
VOICE_OUT = os.environ.get("VOICE_OUT", r"D:\voice-data\out")

DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# ---------------------------------------------------------------- 配置加载

def load_env():
    """读取仓库根目录的 .env（KEY=VALUE，# 开头为注释）。"""
    env = {}
    path = os.path.join(ROOT, ".env")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    # .env wins over pre-existing system variables: a stale key left in the
    # machine's environment must not silently shadow what the user just edited.
    for k, v in env.items():
        if v:
            os.environ[k] = v
    return env


load_env()


def api_key():
    return (os.environ.get("DEEPSEEK_API_KEY") or "").strip()


# ---------------------------------------------------------------- 共享状态

STATE = {
    "teleprompter": "提词器就绪。在中控台生成话术后会显示在这里。",
    "version": 0,
    "product": "",
}
LOCK = threading.Lock()


def set_prompt(text):
    with LOCK:
        STATE["teleprompter"] = text
        STATE["version"] += 1
        return STATE["version"]


# ---------------------------------------------------------------- DeepSeek

COMPLIANCE = (
    "必须遵守中国广告法与平台规则："
    "不用绝对化用语（最好/第一/最便宜/国家级/永久/万能）；"
    "不作医疗功效、治疗、减肥瘦身承诺；不编造销量和权威认证；"
    "不贬低同行；不承诺收益。"
)

PERSONA = (
    "你是一名经验丰富的中文直播带货主播的话术助手。"
    "语言特点：口语化、短句、有节奏感、能调动气氛，像真人在直播间说话，"
    "而不是书面广告文案。可以适度重复关键信息（价格、规格、怎么下单）。"
    + COMPLIANCE
)


def deepseek(messages, temperature=0.8, max_tokens=1200, timeout=90):
    key = api_key()
    if not key:
        raise RuntimeError(
            "没有配置 DEEPSEEK_API_KEY。请把仓库根目录的 .env.example 复制为 .env 并填入密钥。"
        )
    body = json.dumps(
        {
            "model": DEEPSEEK_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        DEEPSEEK_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        raise RuntimeError("DeepSeek 返回 %s：%s" % (e.code, detail))
    except urllib.error.URLError as e:
        raise RuntimeError("连不上 DeepSeek：%s" % e.reason)
    return data["choices"][0]["message"]["content"].strip()


# ---------------------------------------------------------------- 业务动作

def gen_script(product, points, minutes):
    user = (
        "请为下面这个商品写一段直播讲解话术，时长大约 %s 分钟，可以直接照着念。\n"
        "商品：%s\n卖点/规格/价格等信息：%s\n\n"
        "要求：\n"
        "1. 开头 1 句留人（说清在卖什么、给谁用）\n"
        "2. 中间讲 3~4 个卖点，每个卖点配一个生活化场景\n"
        "3. 自然穿插 2 次价格和下单引导\n"
        "4. 结尾一句催单\n"
        "5. 分段输出，每段一两句话，方便提词器滚动\n"
        "只输出话术正文，不要标题和解释。"
    ) % (minutes, product, points or "（未提供，请合理假设并保持中性，不要编造认证和销量）")
    return deepseek([
        {"role": "system", "content": PERSONA},
        {"role": "user", "content": user},
    ])


def gen_qa(product, points, count):
    user = (
        "为下面这个商品准备直播间常见问答，共 %s 条，覆盖价格、规格尺码、材质、"
        "发货时效、售后退换、怎么下单、适用人群等。\n"
        "商品：%s\n已知信息：%s\n\n"
        "每条格式严格为：\nQ: 观众问题\nA: 主播回答（口语、1~2 句、直接能念）\n"
        "不确定的信息用「以商品详情页为准」这类稳妥说法，不要编造。"
    ) % (count, product, points or "（未提供）")
    return deepseek([
        {"role": "system", "content": PERSONA},
        {"role": "user", "content": user},
    ])


def make_voice(text, voice, rate, pitch):
    """文字 -> 卖家音色 wav。走 tts_to_voice.py（edge-tts + RVC），不需要麦克风。"""
    import subprocess
    import time as _t

    text = (text or "").strip()
    if not text:
        raise RuntimeError("没有可合成的文本")
    os.makedirs(VOICE_OUT, exist_ok=True)
    name = "voice_%d.wav" % int(_t.time())
    out = os.path.join(VOICE_OUT, name)
    cmd = [
        sys.executable,
        os.path.join(HERE, "tts_to_voice.py"),
        "--text", text,
        "--out", out,
        "--voice", voice or "zh-CN-XiaoxiaoNeural",
        "--rate", rate or "+8%",
        "--pitch", str(int(pitch or 0)),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=900)
    log = ((r.stdout or "") + (r.stderr or "")).strip()
    if r.returncode != 0 or not os.path.isfile(out):
        raise RuntimeError("合成失败：\n" + "\n".join(log.splitlines()[-8:]))
    return name, os.path.getsize(out), log


def gen_reply(product, comment):
    user = (
        "直播间观众发了一条弹幕，请给出主播的口语回应，1~2 句、直接能念出来，"
        "语气热情但不浮夸。如果问的是不确定的信息，就引导看商品详情页或说稍后统一回答。\n"
        "商品：%s\n弹幕：%s\n\n只输出要念的那句话。"
    ) % (product or "（未设置）", comment)
    return deepseek(
        [
            {"role": "system", "content": PERSONA},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
        max_tokens=300,
    )


# ---------------------------------------------------------------- HTTP

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def log_message(self, fmt, *args):
        sys.stderr.write("[console] " + fmt % args + "\n")

    # ---- helpers
    def _send_json(self, obj, code=200):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def _send_file(self, name):
        path = os.path.join(HERE, name)
        try:
            with open(path, "rb") as f:
                raw = f.read()
        except OSError:
            self.send_error(404, "missing %s" % name)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    # ---- routes
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send_file("ui.html")
        if self.path.startswith("/teleprompter"):
            return self._send_file("teleprompter.html")
        if self.path.startswith("/api/current"):
            with LOCK:
                return self._send_json(
                    {"text": STATE["teleprompter"], "version": STATE["version"]}
                )
        if self.path.startswith("/api/health"):
            return self._send_json(
                {"ok": True, "has_key": bool(api_key()), "product": STATE["product"]}
            )
        if self.path.startswith("/voice/"):
            name = os.path.basename(self.path[len("/voice/"):].split("?")[0])
            path = os.path.join(VOICE_OUT, name)
            if not name.endswith(".wav") or not os.path.isfile(path):
                return self.send_error(404, "no such audio")
            with open(path, "rb") as f:
                raw = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return self.wfile.write(raw)
        return super().do_GET()

    def do_POST(self):
        b = self._body()
        try:
            if self.path.startswith("/api/script"):
                txt = gen_script(
                    b.get("product", ""), b.get("points", ""), b.get("minutes", 3)
                )
                with LOCK:
                    STATE["product"] = b.get("product", "")
                set_prompt(txt)
                return self._send_json({"ok": True, "text": txt})

            if self.path.startswith("/api/qa"):
                txt = gen_qa(
                    b.get("product", ""), b.get("points", ""), b.get("count", 12)
                )
                return self._send_json({"ok": True, "text": txt})

            if self.path.startswith("/api/reply"):
                txt = gen_reply(b.get("product") or STATE["product"], b.get("comment", ""))
                return self._send_json({"ok": True, "text": txt})

            if self.path.startswith("/api/current"):
                v = set_prompt(b.get("text", ""))
                return self._send_json({"ok": True, "version": v})

            if self.path.startswith("/api/voice"):
                name, size, log = make_voice(
                    b.get("text", ""),
                    b.get("voice", "zh-CN-XiaoxiaoNeural"),
                    b.get("rate", "+8%"),
                    b.get("pitch", 0),
                )
                return self._send_json(
                    {"ok": True, "file": name, "size": size, "url": "/voice/" + name}
                )

            if self.path.startswith("/api/product"):
                with LOCK:
                    STATE["product"] = b.get("product", "")
                return self._send_json({"ok": True})

            return self._send_json({"ok": False, "error": "unknown route"}, 404)
        except Exception as e:
            return self._send_json({"ok": False, "error": str(e)}, 500)


def main():
    print("=" * 62)
    print(" 直播中控台")
    print(" 控制台   : http://127.0.0.1:%d" % PORT)
    print(" 提词器   : http://127.0.0.1:%d/teleprompter   (OBS 浏览器源用这个)" % PORT)
    print(" DeepSeek : %s" % ("已配置密钥" if api_key() else "!! 未配置，请在 .env 填 DEEPSEEK_API_KEY"))
    print("=" * 62)
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
        srv.server_close()


if __name__ == "__main__":
    main()
