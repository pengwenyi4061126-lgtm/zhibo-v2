# Python 环境已统一到 3.12

机器上原来装的 **Python 3.14 已彻底卸载**,全部统一到 **3.12**。

## 为什么要统一到 3.12

3.14 太新,AI/ML 生态基本还没有它的预编译轮子:
- `onnxruntime-gpu`、`insightface`、`torch` 等都没有 cp314 的包
- RVC 整合包自带的运行时本来就是 3.12
- 换脸(Deep-Live-Cam)的依赖也只认 3.12

两个版本并存只会让"装到哪个 python 了"变成持续的坑。

## 现在的环境布局

| 用途 | 解释器 | 说明 |
|---|---|---|
| **通用 / 默认 `python`** | `D:\py312\python\python.exe` | 3.12.16,已加入 PATH,`pip` 可用 |
| **变声 RVC** | `D:\RVC\RVC20260718Nvidia\runtime\python.exe` | 3.12.10,整合包自带,**专用别动** |
| **换脸 Deep-Live-Cam** | `D:\DeepLiveCam\.venv\Scripts\python.exe` | 基于 3.12.16 的独立 venv |

> 后两个是**各自隔离**的:RVC 要 numpy 1.x,换脸要 numpy 2.x,混在一起会互相破坏。

## 卸载 3.14 时做过的处理(没丢东西)

1. **工具链迁移** —— 3.14 里装的 33 个包全部重装到 3.12 并通过导入自检:
   `frida 17.25.0`、`playwright`、`capstone`、`keystone-engine`、`pyelftools`、
   `vmlinux-to-elf`、`cryptography`、`pycryptodome`、`python-docx`、`lxml`、
   `requests`、`PyYAML`、`pillow`、`ddgs` 等。
2. **Codex MCP 重新指向** —— `C:\Users\Administrator\.codex\config.toml` 里
   `[mcp_servers.deepseek]` 的 `command` 从 3.14 改为 `D:\py312\python\python.exe`
   (该脚本只用标准库,无需额外依赖)。原配置已备份为 `config.toml.bak-py312-*`。
3. **PATH** —— 用户 PATH 的 3.14 条目换成 `D:\py312\python\` + `Scripts\`;
   系统 PATH 的 3.14 条目由卸载程序自行清除。修改前已备份到 `D:\env_backup\`。
4. **卸载** —— 用官方卸载器静默卸载,注册表 10 条相关条目全部清零,残留的
   `Lib\site-packages`(383MB)一并删除。

## 还需你留意

| 事项 | 说明 |
|---|---|
| **重启终端** | 已开着的终端/IDE 还持有旧环境变量,新开一个窗口 `python` 才会指到 3.12 |
| **PyCharm** | 项目解释器可能还指向已删除的 3.14,需改成 `D:\py312\python\python.exe` |
| **playwright 浏览器** | 包装好了,但浏览器内核要另外下:`python -m playwright install`(约 400MB) |
| 空壳目录 | `D:\Python\pyhton3.14\Scripts` 这个空文件夹被占用删不掉,重启后可手动删 |
