# 第一步：RVC 变声验证（按你这台机器定制）

> 目标：用现成人声数据，训一个"卖家音色"的 RVC 模型，再用实时变声验证 **像不像 + 延迟**。
> 这一步过了，整条路就成立；不过就先调这。

## 0. 现状（已核对）

| 项 | 实况 | 影响 |
|---|---|---|
| 显卡 | GTX 1050 Ti / **4GB** / 驱动 560.94 | 能训能实时跑，但显存小 → 批次要调小 |
| 数据 | `D:\voice-data\sliced`：139 段 wav，**32kHz / 单声道 / 16bit，≈14.4 分钟** | 干净人声，够训一版（RVC ≤10 分钟即可） |
| Python | 系统默认 **3.14**（另有 3.11） | ⚠ 3.14 太新，PyTorch/RVC 不支持 → **别用它，走整合包** |

## 1. 装 RVC（用整合包，别 pip 装进 3.14）

- 官方仓库：<https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI>
- 下载页（Windows 整合包 / 实时插件）：<https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI/releases>
- 活跃维护分支（可选）：<https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI>

解压后双击 `go-web.bat` 启动，浏览器开 WebUI。**整合包自带 Python + 依赖 + ffmpeg，和系统的 3.14 / 3.11 互不干扰。**

## 2. 训练（4GB 显存参数）

WebUI「训练」页，依次：

1. 实验名：`seller`
2. 目标采样率：**40k**（v2）—— 源是 32k，训 48k 没增益，40k 最稳
3. 版本：**v2**
4. 训练数据路径：`D:\voice-data\sliced`
5. 音高提取算法：**rmvpe**（最准，推荐）
6. **batch size：先设 4**；若报 `CUDA out of memory`，降到 2 或 1
7. 总轮数：先 **100~150**，每 10~20 轮存一次
8. 顺序点：**处理数据 → 特征提取 → 训练模型 → 训练索引**

产出：模型 `seller.pth` + 索引 `added_*.index`（建议统一放 `D:\voice-data\models\`）。

> 4GB 训练偏慢；若太慢或老 OOM，可租卡训（AutoDL 等），模型拿回本地用。

## 3. 实时变声（验证）

- 工具：**w-okada voice-changer**：<https://github.com/w-okada/voice-changer>
  或官方 RVC 实时 GUI / VST 插件（在上面 releases 里）。
- 载入 `seller.pth` + `.index`。
- 输入：麦克风；输出：虚拟声卡（VB-CABLE）→ 再接进 OBS 音频源。
- 调 index rate / 清辅音保护 / chunk 块大小，平衡 **像不像 ↔ 延迟**。

## 4. 判据

| 结果 | 下一步 |
|---|---|
| 像 + 延迟可接受 ✅ | 进阶段二（Deep-Live-Cam 换脸 + OBS） |
| 不够像 | 加数据 / 调轮数 / 确认 rmvpe / 提高 index rate |
| 延迟大 | 调小 chunk、关多余特效；1050Ti 实时一般 150~300ms，够用不极致 |

## 来源（版本会变，以官方为准）

- RVC 官方仓库 / Releases / fumiama 分支
- w-okada voice-changer（实时客户端）
