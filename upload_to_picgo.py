#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pikachu 靶场笔记 - 图片批量上传脚本
=====================================
功能：
  1. 解压 docx，提取所有图片
  2. 逐张调用 PicGo HTTP API 上传到 GitHub 图床
  3. 获取 jsDelivr CDN 链接
  4. 替换 MD 文件中的 media/imageX.png 为真实链接
  5. 输出新的 MD 文件

使用前提：
  - PicGo 已启动，Server 已开启（端口 36677）
  - GitHub 图床已配置好

使用方法：
  python upload_to_picgo.py

  脚本会自动寻找同目录下的 pikachu.docx 和 pikachu靶场笔记.md
  也可以手动修改下方 DOCX_PATH 和 MD_PATH 变量
"""

import os
import re
import json
import time
import shutil
import zipfile
import requests
import tempfile

# ========== 配置区（按需修改） ==========
PICGO_API   = "http://127.0.0.1:36677/upload"   # PicGo Server 地址
CDN_BASE    = "https://cdn.jsdelivr.net/gh/Tjsdrj/BlogImage@main/img"  # 最终链接前缀

# 文件路径（修改为你自己的路径）
DOCX_PATH   = "pikachu.docx"          # 原始 docx 文件
MD_PATH     = "pikachu靶场笔记.md"     # 要处理的 MD 文件
OUTPUT_MD   = "pikachu靶场笔记_图床版.md"  # 输出的新 MD 文件
# =========================================


def extract_images_from_docx(docx_path: str, output_dir: str) -> dict:
    """
    从 docx 中提取所有图片，返回 {原始名: 临时文件路径} 的映射
    """
    print(f"📂 正在解压 {docx_path} 提取图片...")
    image_map = {}

    with zipfile.ZipFile(docx_path, 'r') as z:
        media_files = [f for f in z.namelist() if f.startswith("word/media/")]
        if not media_files:
            print("⚠️  docx 中没有找到图片！")
            return image_map

        # 用 docx 文件名作为前缀，避免不同文章图片重名
        docx_prefix = os.path.splitext(os.path.basename(docx_path))[0]  # e.g. "pikachu"

        for media_path in media_files:
            filename = os.path.basename(media_path)  # e.g. image1.png
            if not filename:  # 跳过空目录条目
                continue
            name, ext = os.path.splitext(filename)        # "image1", ".png"
            new_filename = f"{docx_prefix}_{name}{ext}"   # "pikachu_image1.png"
            dest = os.path.join(output_dir, new_filename)
            with z.open(media_path) as src, open(dest, 'wb') as dst:
                dst.write(src.read())
            # MD 里引用的是 media/image1.png，映射到重命名后的文件
            image_map[f"media/{filename}"] = dest

    print(f"✅ 共提取 {len(image_map)} 张图片\n")
    return image_map


def upload_via_picgo(file_path: str) -> str | None:
    """
    调用 PicGo HTTP API 上传单张图片，返回 CDN URL 或 None
    """
    try:
        payload = {"list": [file_path]}
        resp = requests.post(PICGO_API, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # PicGo 返回格式: {"success": true, "result": ["url1", ...]}
        if data.get("success") and data.get("result"):
            return data["result"][0]
        else:
            print(f"    ❌ PicGo 返回失败: {data}")
            return None
    except requests.exceptions.ConnectionError:
        print("    ❌ 无法连接 PicGo Server，请确认 PicGo 已启动且 Server 已开启（端口 36677）")
        return None
    except Exception as e:
        print(f"    ❌ 上传出错: {e}")
        return None


def replace_links_in_md(md_path: str, link_map: dict, output_path: str):
    """
    读取 MD 文件，替换所有图片链接，写入新文件
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    replaced = 0
    for original_ref, new_url in link_map.items():
        if original_ref in content:
            content = content.replace(original_ref, new_url)
            replaced += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n✅ 已替换 {replaced} 处图片链接")
    print(f"📄 新 MD 文件已保存至：{output_path}")


def main():
    print("=" * 55)
    print("  🐾 Pikachu 靶场笔记 - 图片批量上传工具")
    print("=" * 55)

    # 检查文件是否存在
    if not os.path.exists(DOCX_PATH):
        print(f"❌ 找不到 docx 文件：{DOCX_PATH}")
        print("   请把脚本和 docx 放在同一目录，或修改脚本顶部的 DOCX_PATH")
        return

    if not os.path.exists(MD_PATH):
        print(f"❌ 找不到 MD 文件：{MD_PATH}")
        print("   请把脚本和 MD 文件放在同一目录，或修改脚本顶部的 MD_PATH")
        return

    # 创建临时目录存放图片
    tmp_dir = tempfile.mkdtemp(prefix="pikachu_imgs_")

    try:
        # Step 1: 提取图片
        image_map = extract_images_from_docx(DOCX_PATH, tmp_dir)
        if not image_map:
            return

        # Step 2: 逐张上传
        print("🚀 开始上传图片到 PicGo...\n")
        link_map = {}   # {media/imageX.png: CDN链接}
        success = 0
        failed = []

        for idx, (ref, file_path) in enumerate(sorted(image_map.items()), 1):
            filename = os.path.basename(file_path)
            print(f"  [{idx:02d}/{len(image_map)}] 上传 {filename} ...", end=" ", flush=True)

            url = upload_via_picgo(file_path)
            if url:
                # 统一转为 jsDelivr CDN 链接（PicGo 返回的可能是 raw.githubusercontent.com）
                # 如果已经是 CDN 链接就直接用，否则拼接
                if "cdn.jsdelivr.net" in url or "github.com" not in url:
                    cdn_url = url
                else:
                    cdn_url = f"{CDN_BASE}/{filename}"

                link_map[ref] = cdn_url
                print(f"✅ {cdn_url}")
                success += 1
            else:
                failed.append(ref)
                print(f"❌ 跳过")

            # 避免请求过快
            time.sleep(0.3)

        # Step 3: 替换 MD 链接
        print(f"\n{'='*55}")
        print(f"📊 上传完成：成功 {success} 张，失败 {len(failed)} 张")

        if failed:
            print("\n⚠️  以下图片上传失败，链接未替换：")
            for f in failed:
                print(f"   - {f}")

        replace_links_in_md(MD_PATH, link_map, OUTPUT_MD)

        print(f"\n🎉 全部完成！请使用 {OUTPUT_MD}")

    finally:
        # 清理临时文件
        shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
