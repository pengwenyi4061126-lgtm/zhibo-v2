# zhibo · 真人实时换脸变声直播

真人实时出镜 + **实时换脸**（本人脸）+ **实时变声**（本人音色）+ OBS → 推流抖音 的半无人带货直播项目。
全新开始的 v2（旧项目存档在 `github.com/cctv202612/zhibo`）。

## 快速开始

1. 读方案：[`新项目方案.md`](新项目方案.md)
2. 做第一步（变声验证）：[`docs/01-第一步-RVC变声.md`](docs/01-第一步-RVC变声.md)
3. 配置密钥：复制 `.env.example` 为 `.env` 并填入 DeepSeek key

## 管线

```
真人实时讲 → Deep-Live-Cam 换脸 → RVC 变声 → OBS 合成 → 推流抖音（标注AI）
                                              DeepSeek：话术提词 + 评论助手
```

## 仓库结构

| 路径 | 内容 |
|---|---|
| `新项目方案.md` | 完整方案：架构 / 工具 / 资产 / 路线 / 合规 |
| `docs/01-第一步-RVC变声.md` | 落地第一步：训 RVC + w-okada 实时变声 |
| `docs/合规与防封.md` | 抖音 / 深度合成合规红线 |
| `docs/历史与资产.md` | 旧项目存档、资产位置、来源对话 |
| `.env.example` | API Key 模板（真实 key 放 `.env`，不提交） |

## 关键资产（在工作区外，不入库）

- 人声数据：`D:\voice-data\sliced`
- 源视频：`D:\voice-data\球.spxzq.mp4`
