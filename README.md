# zhibo · 真人实时换脸变声直播

真人实时出镜 + **实时换脸**(本人脸)+ **实时变声**(本人音色)+ OBS 合成 → 推流抖音 的半无人带货直播系统。
全新开始的 v2(旧项目存档在 `github.com/cctv202612/zhibo`)。

## 系统总览

```
真人(你/助理)对着摄像头实时讲
   ├─ 脸：Deep-Live-Cam 实时换成卖家本人的脸
   ├─ 声：RVC 实时转成卖家本人音色  ✅ 已训练完成
   └─→ OBS 合成(产品空镜 / 价格浮层 / AI标注)  ✅ 已安装
         └─→ 推流抖音
中控台：DeepSeek 话术提词 + 问答库 + 评论区助手  ✅ 已做好
```

## 当前进度

| 模块 | 状态 | 位置 |
|---|---|---|
| **变声模型**(卖家音色) | ✅ 训练完成并装好 | `D:\RVC\...\assets\weights\seller.pth` |
| **变声运行环境** | ✅ 已装、GPU 可用 | `D:\RVC\RVC20260718Nvidia\` |
| **AI 中控台** | ✅ 已做好,待填 DeepSeek 密钥 | `console/` |
| **OBS 合成推流** | ✅ 便携版已装 | `D:\OBS\bin\64bit\obs64.exe` |
| **换脸** | ⏳ 已下好模型,待装依赖 | `D:\DeepLiveCam\` |
| **摄像头** | ❌ **本机未检测到,需要补硬件** | — |
| **虚拟声卡 VB-CABLE** | ❌ 需你手动装(要管理员) | [vb-audio.com/Cable](https://vb-audio.com/Cable/) |

## 快速开始

1. **启动中控台**:双击 `启动中控台.bat` → 浏览器开 http://127.0.0.1:8777
   先在 `.env` 填 `DEEPSEEK_API_KEY`(机器里那个旧 key 已失效)。
2. **启动变声**:双击 `D:\RVC\RVC20260718Nvidia\go-realtime_gui.bat`,加载
   `seller.pth` + `added_IVF1026_..._seller_v2.index`。
3. **启动 OBS**:`D:\OBS\bin\64bit\obs64.exe`,按 [`docs/05-OBS合成与推流.md`](docs/05-OBS合成与推流.md) 搭场景。

## 文档

| 文件 | 内容 |
|---|---|
| [`新项目方案.md`](新项目方案.md) | 完整方案:架构 / 工具 / 资产 / 路线 / 合规 |
| [`docs/01-第一步-RVC变声.md`](docs/01-第一步-RVC变声.md) | 变声环境与本机参数 |
| [`docs/02-免费云端训练-Colab.md`](docs/02-免费云端训练-Colab.md) | 免费云端训练(备用路线) |
| [`docs/03-模型已训练完成.md`](docs/03-模型已训练完成.md) | 模型训练结果与踩坑记录 |
| [`docs/04-中控台.md`](docs/04-中控台.md) | 中控台用法(提词/问答库/评论助手) |
| [`docs/05-OBS合成与推流.md`](docs/05-OBS合成与推流.md) | OBS 场景、音频链路、推流抖音 |
| [`docs/合规与防封.md`](docs/合规与防封.md) | 深度合成红线、AI 标注 |
| [`docs/历史与资产.md`](docs/历史与资产.md) | 旧项目存档、资产位置 |

## 关键资产(在工作区外,不入库)

- 人声数据:`D:\voice-data\sliced`
- 源视频:`D:\voice-data\球.spxzq.mp4`
- 训练好的模型备份:`D:\voice-data\models\`
