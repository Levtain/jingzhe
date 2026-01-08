import os
import re
import requests
import argparse
import sys
from urllib.parse import urlparse
from pathlib import Path

def extract_links(md_content):
    """
    提取 Markdown 内容中的链接。
    返回列表: [(title, url), ...]
    """
    links = []
    
    # 1. 匹配标准 Markdown 链接 [title](url)
    # 排除以 ! 开头的图片链接
    md_links = re.findall(r'(?<!\!)\[([^\]]*)\]\((https?://[^\s\)]+)\)', md_content)
    links.extend(md_links)
    
    # 2. 匹配自动链接 <url>
    auto_links = re.findall(r'<(https?://[^>]+)>', md_content)
    for url in auto_links:
        links.append(("", url))
        
    # 3. 匹配裸链接 (简单的 http 开头，空格或换行结尾)
    # 注意：这可能会匹配到已经在 markdown 链接中的 url，所以需要去重或更复杂的正则
    # 这里为了简单起见，如果上面没有匹配到的，可以尝试作为裸链接，但为了避免重复下载，
    # 我们最好先只处理明确的链接格式，或者在下载时去重。
    # 既然用户需求是 "提到的网页"，通常是有上下文的。
    # 为了稳健，我们先只处理前两种明确的格式。
    
    return links

def extract_urls_from_text(text):
    """
    从纯文本中提取 URL (每行一个，或者简单的正则)
    """
    urls = []
    # 匹配 http/https 开头的字符串
    # 排除一些明显的非 URL 字符
    found = re.findall(r'(https?://[^\s<>"`]+)', text)
    for url in found:
        # 清理结尾的标点 (括号、方括号、逗号、分号、点、反引号)
        url = url.rstrip('),].;\'')
        if url:
            urls.append(("", url))
    return urls

def sanitize_filename(name):
    """
    清理文件名中的非法字符
    """
    # 替换 windows/linux 下的非法字符
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    # 替换换行符等
    name = re.sub(r'[\r\n\t]', "", name)
    return name.strip()

def get_filename_from_url(url):
    """
    从 URL 中推断文件名
    """
    parsed = urlparse(url)
    path = parsed.path
    name = os.path.basename(path)
    if not name:
        name = parsed.netloc
    
    # 移除查询参数等
    if not name or name == '/':
        name = "index"
        
    return name

def download_url(url, output_dir, title=None):
    """
    下载 URL 内容并保存
    """
    try:
        # 设置 User-Agent 避免被简单的反爬拦截
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        print(f"正在下载: {url} ...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # 确定文件名
        if title:
            filename = sanitize_filename(title)
        else:
            filename = sanitize_filename(get_filename_from_url(url))
            
        # 确保有 .html 后缀 (如果原文件名没有后缀或后缀不是网页相关的)
        if not filename.lower().endswith(('.html', '.htm')):
            filename += '.html'
            
        # 限制文件名长度
        if len(filename) > 200:
            filename = filename[:200] + '.html'

        filepath = os.path.join(output_dir, filename)
        
        # 处理重名：如果文件已存在，添加数字后缀
        counter = 1
        original_filepath = filepath
        base_name, ext = os.path.splitext(filepath)
        while os.path.exists(filepath):
            filepath = f"{base_name}_{counter}{ext}"
            counter += 1

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"✔ 已保存: {filepath}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✘ 下载失败 {url}: {e}")
        return False
    except Exception as e:
        print(f"✘ 保存出错 {url}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="从 Markdown 文件、纯文本文件或命令行参数中批量下载网页")
    parser.add_argument("input", help="输入路径 (Markdown文件/目录/txt文件) 或直接的 URL")
    parser.add_argument("--output", "-o", default="downloaded_pages", help="保存网页的文件夹 (默认为 downloaded_pages)")
    
    args = parser.parse_args()
    
    input_val = args.input
    output_dir = args.output
    
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"创建输出目录: {output_dir}")
        except Exception as e:
            print(f"创建输出目录失败: {e}")
            sys.exit(1)
        
    # 检查输入是否为 URL
    if input_val.startswith("http://") or input_val.startswith("https://"):
        print(f"检测到直接 URL 输入: {input_val}")
        download_url(input_val, output_dir)
        print(f"文件保存在: {os.path.abspath(output_dir)}")
        return

    # 检查输入是否为文件或目录
    md_files = []
    txt_files = []
    
    if os.path.isfile(input_val):
        if input_val.lower().endswith('.md'):
            md_files.append(input_val)
        else:
            # 假设其他文件都是文本文件，尝试按行读取
            txt_files.append(input_val)
    elif os.path.isdir(input_val):
        for root, _, files in os.walk(input_val):
            for file in files:
                if file.lower().endswith('.md'):
                    md_files.append(os.path.join(root, file))
                elif file.lower().endswith('.txt'):
                    txt_files.append(os.path.join(root, file))
    else:
        print(f"错误: 输入路径 '{input_val}' 不存在，且不是有效的 URL")
        sys.exit(1)
        
    if not md_files and not txt_files:
        print("未找到 Markdown 或文本文件")
        sys.exit(0)
        
    total_links = 0
    success_count = 0
    
    seen_urls = set() # 避免重复下载相同的 URL
    
    # 处理 Markdown 文件
    for md_file in md_files:
        print(f"\n正在处理 Markdown 文件: {md_file}")
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            links = extract_links(content)
            if not links:
                print("  - 未找到链接")
                continue
                
            print(f"  - 找到 {len(links)} 个链接")
            
            for title, url in links:
                if url in seen_urls:
                    print(f"  - 跳过重复 URL: {url}")
                    continue
                    
                seen_urls.add(url)
                if download_url(url, output_dir, title):
                    success_count += 1
                total_links += 1
                
        except Exception as e:
            print(f"无法读取文件 {md_file}: {e}")

    # 处理文本文件
    for txt_file in txt_files:
        print(f"\n正在处理文本文件: {txt_file}")
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            links = extract_urls_from_text(content)
            if not links:
                print("  - 未找到链接")
                continue
            
            print(f"  - 找到 {len(links)} 个链接")
            
            for title, url in links:
                if url in seen_urls:
                    print(f"  - 跳过重复 URL: {url}")
                    continue
                
                seen_urls.add(url)
                if download_url(url, output_dir, title):
                    success_count += 1
                total_links += 1

        except Exception as e:
             print(f"无法读取文件 {txt_file}: {e}")

    print(f"\n完成! 共处理 {len(seen_urls)} 个唯一链接，成功下载 {success_count} 个页面。")
    print(f"文件保存在: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
