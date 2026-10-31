#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""文字 -> 卖家音色音频（全程不需要麦克风）。

链路：edge-tts 合成普通话 -> RVC 转成卖家音色 -> 输出 wav

用通用 Python 3.12 运行：
  D:\\py312\\python\\python.exe console\\tts_to_voice.py --text "大家好" --out D:\\voice-data\\out\\demo.wav

为什么这么做：本机是 Windows N 版（无系统语音组件）、且没有麦克风，
所以用 edge-tts 当"声源"，再过 RVC 换成卖家音色。
"""
import argparse
import asyncio
import os
import subprocess
import sys
import tempfile

RVC_ROOT = os.environ.get("RVC_ROOT", r"D:\RVC\RVC20260718Nvidia")
RVC_PY = os.path.join(RVC_ROOT, "runtime", "python.exe")
HERE = os.path.dirname(os.path.abspath(__file__))

DEFAULT_MODEL = "seller.pth"
DEFAULT_INDEX = os.path.join(
    RVC_ROOT, "logs", "seller", "added_IVF1026_Flat_nprobe_1_seller_v2.index"
)


async def synth(text, out_mp3, voice, rate, volume):
    import edge_tts

    tts = edge_tts.Communicate(text, voice, rate=rate, volume=volume)
    await tts.save(out_mp3)


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="要说的话")
    src.add_argument("--text-file", dest="text_file", help="从文件读（UTF-8）")
    ap.add_argument("--out", required=True, help="输出 wav")
    # 默认值 = 实测对标卖家真声后的最优配方（见 docs/10-音色调参.md）
    ap.add_argument("--voice", default="zh-CN-XiaoxiaoNeural",
                    help="TTS 声源。晓晓音高起伏最大(10.8半音)，最接近真人；"
                         "晓伊/云健起伏只有 6~7 半音，听着平")
    ap.add_argument("--rate", default="+10%", help="语速，带货一般 +10% ~ +15%")
    ap.add_argument("--volume", default="+15%")
    ap.add_argument("--pitch", type=int, default=-4,
                    help="RVC 变调半音。-4 实测让 F0 中位落在 202.6Hz，"
                         "与卖家真声(201.2Hz)差 0.1 半音；想更尖用 -2 或 -1")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--index", default=DEFAULT_INDEX)
    ap.add_argument("--index-rate", type=float, default=0.90, dest="index_rate",
                    help="越高越贴近训练音色，实测 0.90 最佳")
    ap.add_argument("--rms-mix-rate", type=float, default=0.25, dest="rms_mix_rate",
                    help="音量包络：0=完全用模型自己的强弱，1=跟随TTS原声。实测 0.25 起伏最接近真人")
    ap.add_argument("--target-rms-db", type=float, default=-17.4, dest="target_rms_db",
                    help="输出音量归一化目标，卖家真声实测 -17.4 dB")
    ap.add_argument("--keep-tts", action="store_true", dest="keep_tts",
                    help="保留中间的 TTS 原声，便于对比")
    args = ap.parse_args()

    text = args.text
    if args.text_file:
        with open(args.text_file, "r", encoding="utf-8") as f:
            text = f.read()
    text = (text or "").strip()
    if not text:
        print("ERROR: 文本是空的")
        return 2

    if not os.path.isfile(RVC_PY):
        print("ERROR: 找不到 RVC 解释器 %s" % RVC_PY)
        return 2

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    # ---- 第 1 步：TTS
    tts_path = (os.path.splitext(out)[0] + "_tts.mp3") if args.keep_tts else os.path.join(
        tempfile.gettempdir(), "zhibo_tts_%d.mp3" % os.getpid()
    )
    print("[1/2] edge-tts 合成（%s, rate=%s）…" % (args.voice, args.rate), flush=True)
    asyncio.run(synth(text, tts_path, args.voice, args.rate, args.volume))
    size = os.path.getsize(tts_path)
    print("      TTS 完成: %s (%d 字节)" % (tts_path, size), flush=True)
    if size < 1000:
        print("ERROR: TTS 输出异常小，可能是网络或声音名不对")
        return 1

    # ---- 第 2 步：RVC 换音色（必须用 RVC 自带解释器）
    print("[2/2] RVC 转成卖家音色…", flush=True)
    cmd = [
        RVC_PY, os.path.join(HERE, "rvc_convert.py"),
        "--input", tts_path,
        "--output", out,
        "--model", args.model,
        "--pitch", str(args.pitch),
        "--index-rate", str(args.index_rate),
        "--rms-mix-rate", str(args.rms_mix_rate),
        "--target-rms-db", str(args.target_rms_db),
    ]
    if args.index and os.path.isfile(args.index):
        cmd += ["--index", args.index]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    tail = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()
    for line in tail[-12:]:
        print("      | " + line, flush=True)

    if not args.keep_tts:
        try:
            os.remove(tts_path)
        except OSError:
            pass

    if r.returncode != 0 or not os.path.isfile(out):
        print("FAILED: RVC 转换没有产出文件")
        return 1
    print("DONE -> %s (%.1f KB)" % (out, os.path.getsize(out) / 1024), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
