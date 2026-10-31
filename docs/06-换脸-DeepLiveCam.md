# 换脸(Deep-Live-Cam)

把镜头前真人的脸,实时换成**卖家本人**的脸。配合已训好的 RVC 变声,就是"真人戴数字面具"。

## 已装好

| 项 | 位置 | 说明 |
|---|---|---|
| Deep-Live-Cam 源码 | `D:\zhibo\runtime\DeepLiveCam\` | 官方仓库 |
| 换脸模型 `inswapper_128_fp16.onnx` | `D:\zhibo\runtime\DeepLiveCam\models\` | 264.8MB |
| 画质增强 `GFPGANv1.4.pth` | `D:\zhibo\runtime\DeepLiveCam\models\` | 332.5MB |
| 独立 Python 3.12.16 | `D:\zhibo\runtime\py312\python\python.exe` | 免安装 |
| 专用虚拟环境 | `D:\zhibo\runtime\DeepLiveCam\.venv\` | **和 RVC 完全隔离** |

> ⚠️ **为什么要单独环境**:Deep-Live-Cam 要 `numpy>=2`,而 RVC 那套用的是 numpy 1.x。
> 装在一起会把刚训好的变声环境搞坏。所以它有自己的 `.venv`,互不干扰。

## 启动

```powershell
& 'D:\zhibo\runtime\DeepLiveCam\.venv\Scripts\python.exe' 'D:\zhibo\runtime\DeepLiveCam\run.py'
```

常用参数:
```powershell
# 用 GPU(1050Ti)
... run.py --execution-provider cuda
```

## 用法(实时模式)

1. **Select a face**:选一张**卖家本人**的清晰正脸照(光线均匀、不戴眼镜遮挡、不侧脸)。
2. 点 **Live**,选摄像头。
3. 勾选项建议(1050Ti 显存只有 4GB,别全开):
   - `Face Enhancer`(GFPGAN 画质增强)**先关掉** —— 很吃显存和帧率,卡就别开
   - `Keep FPS` 打开
4. 把输出接进 OBS:
   - Deep-Live-Cam 若提供虚拟摄像头输出,OBS 里「视频采集设备」选它
   - 否则用 OBS「窗口采集」抓 Deep-Live-Cam 的预览窗口(简单可靠)

## ❗两个前置条件(目前没满足)

| 缺什么 | 影响 | 怎么解决 |
|---|---|---|
| **摄像头** | 实测本机**没有任何摄像头设备**,实时换脸没有画面输入 | 插 USB 摄像头;或手机当摄像头(DroidCam/iVCam);测试期可先用视频文件模式 |
| 源脸照片 | 换成谁的脸 | 准备一张卖家本人清晰正脸照 |

没摄像头之前,可以先用**视频文件**跑一遍验证环境:选源脸 + 选一个目标视频 → Start,看输出效果。

## 1050Ti 性能预期

- inswapper 是 128×128 的轻量模型,4GB 显存够跑。
- 预期 **10~20 FPS**;开 GFPGAN 增强会掉到个位数,**直播别开**。
- 换脸和推流会同时吃显卡 → OBS 编码务必用 **NVENC**,推流 720p~1080p@30。

## 破绽规避(实战经验)

换脸在这几种情况最容易露馅,话术和走位要避开:

- **手挡脸**(比划产品时手从脸前过)→ 尽量在胸口以下展示
- **大幅侧头 / 低头**→ 保持大致正面
- **快速动作**→ 动作放缓
- **强逆光 / 光线突变**→ 固定柔和正面光
- **戴口罩、吃东西**→ 别做

> 这也是为什么"真人实时"这条路反而稳:观众提问时真人直接答,不存在 AI 接不上的卡顿。

## 合规(重要)

- 只能换成**卖家本人**(或**已书面授权**的人)的脸。
- **禁止**冒充任何未授权的特定真人 —— 这是法律红线,不是风格问题。
- 直播间必须有 **AI 标注**。
- 详见 [`合规与防封.md`](合规与防封.md)。
