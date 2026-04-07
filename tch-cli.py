#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 国家中小学智慧教育平台 资源下载工具 CLI 版 (适用于 Termux/Linux)
# 原项目: https://github.com/happycola233/tchMaterial-parser
# 原作者: 肥宅水水呀 (https://space.bilibili.com/324042405)
# cli版作者：chlink2025 (https://github.com/chlink2025)
import os
import sys
import json
import re
import requests
import argparse
import traceback
from pypdf import PdfReader, PdfWriter

VERSION = "v3.3.2-cli"

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "tchMaterial-parser")
CONFIG_FILE = os.path.join(CONFIG_DIR, "data.json")

session = requests.Session()
headers = { "X-ND-AUTH": 'MAC id="0",nonce="0",mac="0"' }
access_token = None

def load_access_token():
    """读取本地存储的 Access Token"""
    global access_token
    if not os.path.exists(CONFIG_FILE):
        return
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        access_token = data.get("access_token")
        if access_token:
            headers["X-ND-AUTH"] = f'MAC id="{access_token}",nonce="0",mac="0"'
    except Exception as e:
        pass

def set_access_token(token: str):
    """设置并保存 Access Token"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = { "access_token": token }
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[*] Access Token 已成功保存至: {CONFIG_FILE}")
    except Exception as e:
        print(f"[!] 保存 Token 失败: {e}")

def parse(url: str, bookmarks: bool):
    """解析资源，获取资源下载链接与目录树"""
    try:
        content_id = None
        content_type = None
        resource_url = None
        chapters = []

        # 提取 URL 参数
        for q in url[url.find("?") + 1:].split("&"):
            if q.split("=")[0] == "contentId":
                content_id = q.split("=")[1]
                break
        if not content_id:
            return None, None, None

        for q in url[url.find("?") + 1:].split("&"):
            if q.split("=")[0] == "contentType":
                content_type = q.split("=")[1]
                break
        if not content_type:
            content_type = "assets_document"

        # 获取资源详情
        if re.search(r"^https?://([^/]+)/syncClassroom/basicWork/detail", url) or content_type == "thematic_course":
            response = session.get(f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/special_edu/resources/details/{content_id}.json")
        else:
            response = session.get(f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/resources/tch_material/details/{content_id}.json")

        data = response.json()
        title = data.get("title")

        # 获取下载链接
        for item in data.get("ti_items", []):
            if item.get("ti_is_source_file"):
                resource_url = item.get("ti_storage")
                if resource_url:
                    resource_url = resource_url.replace("cs_path:${ref-path}", "https://r1-ndr-private.ykt.cbern.com.cn" if access_token else "https://c1.ykt.cbern.com.cn")
                else:
                    resource_url = next((u for u in item.get("ti_storages", []) if u), None)
                
                if not resource_url:
                    continue
                if not access_token:
                    resource_url = re.sub(r"^https?://(?:.+).ykt.cbern.com.cn/(.+)$", r"https://c1.ykt.cbern.com.cn/\1", resource_url)
                break

        # 兜底获取链接 (专题课程逻辑)
        if not resource_url and content_type == "thematic_course":
            resources_resp = session.get(f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrs/special_edu/thematic_course/{content_id}/resources/list.json")
            for resource in resources_resp.json():
                if resource["resource_type_code"] == "assets_document":
                    for item in resource.get("ti_items", []):
                        if item.get("ti_is_source_file"):
                            resource_url = item.get("ti_storage")
                            if resource_url:
                                resource_url = resource_url.replace("cs_path:${ref-path}", "https://r1-ndr-private.ykt.cbern.com.cn" if access_token else "https://c1.ykt.cbern.com.cn")
                            else:
                                resource_url = next((u for u in item.get("ti_storages", []) if u), None)
                            if not resource_url:
                                continue
                            if not access_token:
                                resource_url = re.sub(r"^https?://(?:.+).ykt.cbern.com.cn/(.+)$", r"https://c1.ykt.cbern.com.cn/\1", resource_url)
                            break
                if resource_url:
                    break

        # 获取章节目录
        if bookmarks and resource_url:
            try:
                mapping_url = None
                for item in data.get("ti_items", []):
                    if item.get("ti_file_flag") == "ebook_mapping":
                        mapping_url = item.get("ti_storage")
                        if mapping_url:
                            mapping_url = mapping_url.replace("cs_path:${ref-path}", "https://r1-ndr-private.ykt.cbern.com.cn")
                        else:
                            mapping_url = next((u for u in item.get("ti_storages", []) if u), None)
                        break

                if mapping_url:
                    map_resp = session.get(mapping_url)
                    map_data = map_resp.json()
                    ebook_id = map_data.get("ebook_id")

                    page_map = []
                    if map_data.get("mappings"):
                        for m in map_data["mappings"]:
                            page_map.append({ "node_id": m["node_id"], "page_number": m.get("page_number", 1) })

                    if ebook_id:
                        tree_resp = session.get(f"https://s-file-1.ykt.cbern.com.cn/zxx/ndrv2/national_lesson/trees/{ebook_id}.json", headers=headers)
                        tree_data = tree_resp.json()

                        def process_tree_nodes(nodes):
                            result = []
                            for node in nodes:
                                page_num = next((m["page_number"] for m in page_map if m["node_id"] == node["id"]), None)
                                chapter_item = { "title": node["title"], "page_index": page_num }
                                if node.get("child_nodes"):
                                    chapter_item["children"] = process_tree_nodes(node["child_nodes"])
                                result.append(chapter_item)
                            return result

                        if isinstance(tree_data, list):
                            chapters = process_tree_nodes(tree_data)
                        elif isinstance(tree_data, dict) and tree_data.get("child_nodes"):
                            chapters = process_tree_nodes(tree_data["child_nodes"])

                    if not chapters:
                        page_map.sort(key=lambda x: x["page_number"])
                        for i, m in enumerate(page_map):
                            chapters.append({
                                "title": f"第 {i+1} 节 (P{m['page_number']})",
                                "page_index": m["page_number"]
                            })
            except Exception as e:
                print(f"[!] 获取书签失败: {e}")
                chapters = []

        return resource_url, title, chapters

    except Exception as e:
        print(f"[!] 解析出错: {e}")
        return None, None, None

def download_file(url: str, save_path: str, chapters: list = None):
    """下载文件并显示进度"""
    print(f"[*] 开始下载: {save_path}")
    try:
        response = session.get(url, headers=headers, stream=True)
        if not response.ok:
            reason = "Access Token 可能已过期" if response.status_code in [401, 403] else ""
            print(f"[!] 下载失败: HTTP {response.status_code} {reason}")
            return False

        total_size = int(response.headers.get("Content-Length", 0))
        downloaded_size = 0

        with open(save_path, "wb") as file:
            # 动态分块下载
            chunk_size = 131072 if total_size < 20971520 else 262144 if total_size < 52428800 else 524288
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)
                downloaded_size += len(chunk)
                if total_size > 0:
                    percent = (downloaded_size / total_size) * 100
                    sys.stdout.write(f"\r[*] 进度: {downloaded_size/(1024*1024):.2f}MB / {total_size/(1024*1024):.2f}MB ({percent:.2f}%)")
                    sys.stdout.flush()

        print("\n[*] 下载完成！")
        
        if chapters:
            print("[*] 正在添加书签...")
            add_bookmarks(save_path, chapters)
            print("[*] 书签添加完成！")
        return True

    except Exception as e:
        print(f"\n[!] 下载发生异常: {e}")
        return False

def add_bookmarks(pdf_path: str, chapters: list) -> None:
    """给 PDF 添加书签"""
    try:
        if not chapters:
            return
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        writer.append_pages_from_reader(reader)

        def add_chapter(chapter_list, parent=None):
            for chapter in chapter_list:
                title = chapter.get("title", "未知章节")
                p_index = chapter.get("page_index")
                if p_index is None:
                    continue
                try:
                    page_num = int(p_index) - 1
                except (ValueError, TypeError):
                    continue
                if page_num < 0 or page_num >= len(writer.pages):
                    continue
                bookmark = writer.add_outline_item(title, page_num, parent=parent)
                if chapter.get("children"):
                    add_chapter(chapter["children"], parent=bookmark)

        add_chapter(chapters)
        with open(pdf_path, "wb") as f:
            writer.write(f)
    except Exception as e:
        print(f"[!] 添加书签失败: {e}")

def main():
    parser = argparse.ArgumentParser(description=f"国家中小学智慧教育平台 资源下载工具 {VERSION} (Termux CLI版)")
    parser.add_argument("-t", "--token", help="配置并保存 Access Token (只需运行一次)")
    parser.add_argument("-u", "--url", help="要下载的资源网址")
    parser.add_argument("-f", "--file", help="包含多个资源网址的文本文件 (每行一个 URL)")
    parser.add_argument("-d", "--dir", default=".", help="下载保存的目录路径 (默认为当前目录)")
    parser.add_argument("--no-bookmarks", action="store_true", help="禁用书签添加功能")

    args = parser.parse_args()

    # 处理设置 Token
    if args.token:
        set_access_token(args.token)
        return

    # 没有传入 url 也没有传入文件时打印帮助
    if not args.url and not args.file:
        parser.print_help()
        return

    # 载入 Token
    load_access_token()

    # 收集待下载 URLs
    urls = []
    if args.url:
        urls.append(args.url.strip())
    if args.file:
        if os.path.exists(args.file):
            with open(args.file, "r", encoding="utf-8") as f:
                urls.extend([line.strip() for line in f if line.strip()])
        else:
            print(f"[!] 文件未找到: {args.file}")

    if not os.path.exists(args.dir):
        os.makedirs(args.dir)

    # 循环解析并下载
    for url in urls:
        print(f"\n[-] 正在解析链接: {url}")
        resource_url, title, chapters = parse(url, not args.no_bookmarks)
        
        if not resource_url:
            print("[!] 解析失败。请检查链接是否正确，或验证您的 Access Token 是否有效。")
            continue
        
        # 处理文件名非法字符
        filename = title or "download"
        filename = re.sub(r'[\\/*?:"<>|]', "_", filename) 
        save_path = os.path.join(args.dir, f"{filename}.pdf")

        download_file(resource_url, save_path, chapters if not args.no_bookmarks else None)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] 用户中断操作。")
