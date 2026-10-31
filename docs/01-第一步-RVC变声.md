# 第一步：RVC 变声验证（按你这台机器定制）

> 目标：用现成人声数据，训一个"卖家音色"的 RVC 模型，再用实时变声验证 **像不像 + 延迟**。
> 这一步过了，整条路就成立。

## 0. 安装状态：已完成并验证 ✅

官方整合包已装好，GPU 实测可用：

| 项 | 实况 |
|---|---|
| 安装路径 | `D:\RVC\RVC20260718Nvidia\` |
| 运行时 | **自带** Python 3.12.10 + PyTorch 2.7.1 + CUDA 11.8（不碰系统的 3.14/3.11） |
| 显卡 | GTX 1050 Ti，CUDA 可用（`torch.cuda.is_available() = True`） |
| 模型 | hubert_base（`assets/hubert_base/`，HF 格式 189MB）、rmvpe、pretrained_v2（f0D40k/f0G40k）全就位 |
| 数据 | `D:\voice-data\sliced`：139 段 wav，32kHz 单声道，≈14.4 分钟 |

启动器（都在安装根目录）：
- `go-webui.bat` —— 训练 / 推理 WebUI
- `go-realtime_gui.bat` —— **内置实时变声 GUI**（本包自带，无需再装 w-okada）

## 1. 训练（4GB 显存参数）

双击 `D:\RVC\RVC20260718Nvidia\go-webui.bat` → 浏览器开 WebUI →「训练」页：

1. 实验名：`seller`
2. 版本 **v2**；目标采样率 **40k**（源是 32k，训 48k 无增益）
3. 训练数据路径：`D:\voice-data\sliced`
4. 音高提取：**rmvpe**
5. **batch size：先 4**；报 `CUDA out of memory` 就降到 2 或 1
6. 轮数：100~150，每 10~20 轮存一次
7. 依次点：**处理数据 → 特征提取 → 训练模型 → 训练索引**
8. 产出：`assets/weights/seller.pth` + `logs/seller/added_*.index`

## 2. 实时变声验证（内置 GUI）

双击 `go-realtime_gui.bat` → 载入 `seller.pth` + `.index` → 输入选麦克风、输出选虚拟声卡（VB-CABLE）→ 再接进 OBS 音频源。
调 index rate / 清辅音保护 / chunk 块大小，平衡 **像不像 ↔ 延迟**。

## 3. 判据

| 结果 | 下一步 |
|---|---|
| 像 + 延迟可接受 ✅ | 进阶段二（Deep-Live-Cam 换脸 + OBS） |
| 不够像 | 加数据 / 调轮数 / 提高 index rate |
| 延迟大 | 调小 chunk；1050Ti 实时一般 150~300ms，够用不极致 |

## 来源

- 整合包：HuggingFace `lj1995/VoiceConversionWebUI` → `RVC20260718Nvidia.7z`
- 官方仓库：`github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI`
