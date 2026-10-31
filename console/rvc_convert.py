#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把一段音频转成卖家音色（RVC 推理）。

必须用 RVC 整合包自带的解释器运行：
  D:\\RVC\\RVC20260718Nvidia\\runtime\\python.exe console\\rvc_convert.py --input a.mp3 --output b.wav
"""
import argparse
import os
import sys

RVC_ROOT = os.environ.get("RVC_ROOT", r"D:\RVC\RVC20260718Nvidia")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="输入音频（wav/mp3 都行，内部走 ffmpeg）")
    ap.add_argument("--output", required=True, help="输出 wav")
    ap.add_argument("--model", default="seller.pth", help="assets/weights 下的模型文件名")
    ap.add_argument("--index", default="", help="特征索引 .index 的完整路径（可空）")
    ap.add_argument("--pitch", type=int, default=0, help="变调半音，男声配女声TTS常用 -12 ~ -6")
    ap.add_argument("--f0-method", default="rmvpe", dest="f0_method")
    ap.add_argument("--index-rate", type=float, default=0.75, dest="index_rate")
    ap.add_argument("--rms-mix-rate", type=float, default=0.25, dest="rms_mix_rate")
    ap.add_argument("--protect", type=float, default=0.33, help="保护清辅音，防电音")
    ap.add_argument("--target-rms-db", type=float, default=None, dest="target_rms_db",
                    help="把输出音量归一化到该 dB（卖家真声实测 -17.4）")
    args = ap.parse_args()

    # RVC 的模块都按仓库根目录组织，必须切到那里再导入
    os.chdir(RVC_ROOT)
    sys.path.insert(0, RVC_ROOT)

    # configs.config.Config 自己也会 argparse sys.argv（--port/--pycmd/--dml…），
    # 不清掉的话它会把本脚本的参数当成非法输入直接退出。
    sys.argv = [sys.argv[0]]

    # webui.py 在导入前设置的这些环境变量，RVC 内部靠它们定位模型目录；
    # 不设的话权重路径会变成 "None/seller.pth"。
    os.environ["RVC_CUDA_GRAPH"] = "0"
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
    os.environ.setdefault("weight_root", "assets/weights")
    os.environ.setdefault("weight_pymss_root", "assets/pymss_weights")
    os.environ.setdefault("index_root", "logs")
    os.environ.setdefault("outside_index_root", "assets/indices")
    os.environ.setdefault("rmvpe_root", "assets/rmvpe")
    tmp = os.path.join(RVC_ROOT, "TEMP")
    os.makedirs(tmp, exist_ok=True)
    os.environ["TEMP"] = tmp

    from scipy.io import wavfile  # noqa: E402
    from configs.config import Config  # noqa: E402
    from infer.vc.modules import VC  # noqa: E402

    cfg = Config()
    vc = VC(cfg)
    vc.get_vc(args.model)

    status, result = vc.vc_single(
        0,
        os.path.abspath(args.input),
        args.pitch,
        args.f0_method,
        args.index,
        args.index_rate,
        0,
        args.rms_mix_rate,
        args.protect,
    )
    sr, audio = result if isinstance(result, tuple) else (None, None)
    if audio is None:
        print("CONVERT_FAILED: %s" % (status,), flush=True)
        return 1

    # 对齐音量：RVC 输出普遍比真人素材轻，直播里听起来就"没劲"
    if args.target_rms_db is not None:
        import numpy as np

        a = audio.astype(np.float32)
        peak = float(np.abs(a).max()) or 1.0
        a = a / peak  # 先归一到 [-1,1] 便于按 dB 计算
        rms = float(np.sqrt(np.mean(a ** 2)))
        if rms > 1e-9:
            gain = (10.0 ** (args.target_rms_db / 20.0)) / rms
            a = a * gain
            clipped = int(np.sum(np.abs(a) > 1.0))
            if clipped:
                a = a / float(np.abs(a).max())  # 防削波
                print("NOTE: 增益后有 %d 个采样点溢出，已整体回缩" % clipped, flush=True)
        audio = (a * 32767.0).astype(np.int16)

    out = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    wavfile.write(out, sr, audio)
    print("CONVERT_OK sr=%s samples=%s -> %s" % (sr, len(audio), out), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
