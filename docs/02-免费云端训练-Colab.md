# 免费云端训练 RVC 模型(Google Colab · 免费 T4)

> 本地 1050Ti 训练要 ~20 小时,不现实。用 Colab 免费 T4 训练只要 ~20–40 分钟,0 元。
> **只有"训练"这一步上云;训练出的 `seller.pth` 拿回本地,实时变声在你 1050Ti 上照跑。**

## 0. 准备

- 开 **Clash**(全局或规则模式),确保能打开 Google。
- 一个 Google 账号(Colab + Google Drive 同一个)。
- 数据集已打包:`D:\voice-data\seller_dataset.zip`(45.8MB,139 段人声)。

## 1. 把数据和资产放进 Google Drive

1. 打开 https://drive.google.com ,把 **`seller_dataset.zip` 上传到"我的云端硬盘"根目录**。
2. 开 **Download Training Assets** notebook(它会把 RVC 工程包 `KiwKiw.zip` 下到你的 Drive):
   `https://colab.research.google.com/github/ardha27/AI-Song-Cover-RVC/blob/main/Download_Training_Assets.ipynb`
   → 菜单 **代码执行程序 → 全部运行**。跑完 Drive 里会出现 `assets/KiwKiw.zip`。

## 2. 打开训练 notebook

`https://colab.research.google.com/github/ardha27/AI-Song-Cover-RVC/blob/main/TrainingV2_NoUI.ipynb`

先确认用的是 GPU:菜单 **代码执行程序 → 更改运行时类型 → T4 GPU**。

按顺序运行这些单元格:

1. **Mount Drive**(挂载云端硬盘,会弹授权)
2. **Unzip File From Drive**(解压 KiwKiw 工程 + 装依赖,耗时几分钟)
3. **解压你的数据集**——在该单元格后面新建一个代码单元,粘贴并运行:
   ```python
   !mkdir -p /content/dataset/seller
   !unzip -n /content/drive/MyDrive/seller_dataset.zip -d /content/dataset/seller
   !ls /content/dataset/seller | head
   ```
4.(**若后面报 av / fairseq / numpy 之类的错再回来跑这个补丁**;不报错可跳过)
   ```python
   !pip -q install av praat-parselmouth pyworld faiss-cpu transformers soundfile pyngrok
   !wget -q https://raw.githubusercontent.com/webvijayi/rvc-free-colab/main/apply_fixes.py
   !python apply_fixes.py /content/KiwKiw
   ```

## 3. 「Create Model Folder」单元格——按这个填

| 变量 | 填 |
|---|---|
| `model_name` | `seller` |
| `dataset` | `/content/dataset/seller` |
| `sample_rate` | `40000` |
| `version` | `v2` |
| `f0method` | `rmvpe_gpu` |
| `save_frequency` | `50` |
| `epoch` | `200` |
| `batch_size` | `12`(T4 16G 够;报显存就降到 8) |
| `cache_gpu` | ✅ 勾选 |

## 4. 依次运行(跳过任何 "Open GUI / Gradio" 单元格——免费版会被封)

1. **Preprocess**(数据切分)
2. **Extract Feature**(F0 + HuBERT 特征)
3. **Train Index**(训练索引)
4. **Train Model**(训练;日志会刷 loss,T4 上 200 轮约 20–40 分钟)

## 5. 取回模型

训练完,在 `/content/KiwKiw/logs/seller/` 和 `/content/KiwKiw/assets/weights/` 里:
- 模型:`seller.pth`(或 `seller_e200_...pth` / `G_xxxx.pth` 里最终那个小模型,通常在 `assets/weights/seller.pth`)
- 索引:`added_*.index`

新建单元格打包下载(或存回 Drive):
```python
from google.colab import files
import glob, shutil, os
os.makedirs('/content/out', exist_ok=True)
for p in glob.glob('/content/KiwKiw/assets/weights/seller*.pth') + glob.glob('/content/KiwKiw/logs/seller/added_*.index'):
    shutil.copy(p, '/content/out')
shutil.make_archive('/content/seller_model', 'zip', '/content/out')
files.download('/content/seller_model.zip')   # 或者直接存 Drive: shutil.copy(..., '/content/drive/MyDrive/')
```

## 6. 拿回本地用

解压 `seller_model.zip`,把:
- `seller.pth` → 放到 `D:\RVC\RVC20260718Nvidia\assets\weights\`
- `added_*.index` → 放到 `D:\RVC\RVC20260718Nvidia\logs\seller\`

然后双击 `D:\RVC\RVC20260718Nvidia\go-realtime_gui.bat`,加载 `seller.pth` + 索引,麦克风进、虚拟声卡出 → 接 OBS。实时变声在 1050Ti 上够用。

---

**任何一步报错**:把**整段报错**贴给我,我直接帮你改(这套代码我已经很熟)。常见坑都在第 2.4 步那个补丁里。
