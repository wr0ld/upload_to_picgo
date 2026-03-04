# 🚀 docx2md-picgo：Word 文档图片一键上传图床工具

> 写完笔记导出 Word，图片全是 `media/image1.png` 本地路径？发到博客全部裂图？这个脚本帮你一条命令搞定。

---

## 📖 简介

`upload_to_picgo.py` 是一个专为博客写作者设计的自动化脚本。

很多人习惯用 Word（.docx）写笔记，再转成 Markdown 发布博客。但转换后图片路径全是 `media/image1.png` 这类本地引用，上传到博客后图片全部无法显示。手动一张张上传图床再替换链接，91 张图就要操作 91 次，极其繁琐。

这个脚本配合 **PicGo + GitHub 图床**，实现全程自动化：

```
Word 文档  →  提取图片  →  PicGo 上传  →  CDN 链接  →  新 MD 文件
```

一条命令，所有图片自动上传并替换链接，直接得到可发布的 Markdown 文件。

---

## ✨ 功能特性

- 📦 **自动解压 docx**，无需手动操作，直接从 Word 文件提取图片
- 🖼️ **智能重命名**，图片自动加上文章名前缀（如 `pikachu_image1.png`），多篇文章不会相互覆盖
- 🚀 **调用 PicGo 本地 API**，无需填写 Token，利用已有图床配置直接上传
- 🌐 **自动替换为 CDN 链接**，支持 jsDelivr 加速
- 📄 **生成新 MD 文件**，原文件保留不动，输出带图床链接的新文件
- ⚠️ **失败提示**，上传失败的图片会单独列出，不影响其他图片

---

## 🔧 适用场景

| 场景                    | 说明                                |
| ----------------------- | ----------------------------------- |
| 靶场 / CTF 笔记         | Word 截图多，图片量大，手动替换极慢 |
| 技术博客写作            | 习惯用 Word 打草稿，最终发 Markdown |
| 渗透测试报告            | 大量截图需要整理上传                |
| 任何 docx → MD 的工作流 | 只要有图片都适用                    |

---

## 📋 前置要求

**软件：**

- Python 3.10+
- [PicGo](https://github.com/Molunerfinn/PicGo)（需要启动并开启 Server）

**PicGo 配置：**

- GitHub 图床已配置（仓库、分支、Token、存储路径）
- PicGo-Server 已开启，端口默认 `36677`

> 检查方法：PicGo → 设置 → PicGo-Server → 确认开关为「开」

**Python 依赖：**

```bash
pip install requests
```

---

## ⚙️ 配置说明

打开脚本，修改顶部配置区的变量：

```python
# ========== 配置区（按需修改） ==========
PICGO_API = "http://127.0.0.1:36677/upload"   # PicGo Server 地址，一般不用改
CDN_BASE  = "https://cdn.jsdelivr.net/gh/你的用户名/你的仓库@main/img"  # 改成你自己的

DOCX_PATH = "pikachu.docx"           # Word 文件名
MD_PATH   = "pikachu靶场笔记.md"      # 转换好的 MD 文件名
OUTPUT_MD = "pikachu靶场笔记_图床版.md"  # 输出文件名
```

**CDN_BASE 格式：**

```
https://cdn.jsdelivr.net/gh/GitHub用户名/仓库名@分支名/存储路径
```

例如：

```

```

---

## 🚀 使用教程

### Step 1：准备文件

将以下文件放到**同一个文件夹**：

```
📁 你的文章文件夹/
├── upload_to_picgo.py    ← 本脚本
├── pikachu.docx          ← 原始 Word 文件
└── pikachu靶场笔记.md    ← 已转换好的 MD 文件
```

> MD 文件可以用 Pandoc 转换：`pandoc pikachu.docx -o pikachu靶场笔记.md`

### Step 2：修改配置

打开 `upload_to_picgo.py`，修改配置区的文件名和 CDN 地址。

### Step 3：启动 PicGo

确保 PicGo 正在运行，Server 开关已打开。

### Step 4：运行脚本

```bash
cd 你的文章文件夹
python upload_to_picgo.py
```

### Step 5：查看输出

```
=======================================================
  🐾 Pikachu 靶场笔记 - 图片批量上传工具
=======================================================
📂 正在解压 pikachu.docx 提取图片...
✅ 共提取 91 张图片

🚀 开始上传图片到 PicGo...

  [01/91] 上传 pikachu_image1.png ... ✅ https://cdn.jsdelivr.net/gh/...
  [02/91] 上传 pikachu_image2.png ... ✅ https://cdn.jsdelivr.net/gh/...
  ...

=======================================================
📊 上传完成：成功 91 张，失败 0 张
✅ 已替换 91 处图片链接
📄 新 MD 文件已保存至：pikachu靶场笔记_图床版.md

🎉 全部完成！
```

得到 `pikachu靶场笔记_图床版.md`，图片全部替换为 CDN 链接，直接发博客 ✅

---

## 🔄 复用到其他文章

每次写新文章，只需修改配置区三行：

```python
DOCX_PATH = "sqlmap.docx"
MD_PATH   = "sqlmap笔记.md"
OUTPUT_MD = "sqlmap笔记_图床版.md"
```

图片会自动命名为 `sqlmap_image1.png`、`sqlmap_image2.png`，与其他文章完全隔离，不会覆盖。

---

## ❓ 常见问题

**Q：提示「无法连接 PicGo Server」**

确认 PicGo 正在运行，且 PicGo-Server 开关已打开，端口为 `36677`。

**Q：提示「找不到 docx 文件」**

确认脚本和 docx 在同一目录，或在配置区填写完整路径，例如：

```python
DOCX_PATH = r"D:\Backup\桌面\pikachu\pikachu.docx"
```

**Q：图片上传成功但 MD 里链接没变**

检查 MD 文件中图片引用格式是否为 `media/imageX.png`，其他格式暂不支持。

**Q：部分图片上传失败怎么办**

脚本会在最后列出所有失败的图片名，手动用 PicGo 上传这几张后，在 MD 里手动替换即可。

---

## 📦 获取脚本

```bash
# 直接下载
https://github.com/Tjsdrj/BlogImage  # 或你存放的仓库地址
```

---

## 📄 License

MIT License，自由使用和修改。

---

> 💡 **推荐工作流：** Word 写稿 → Pandoc 转 MD → 本脚本上传图片 → 发布博客，三步完成从笔记到博文的全流程。
