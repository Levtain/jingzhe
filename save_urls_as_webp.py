import os
import sys
import argparse
import time
import io
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from PIL import Image

# 尝试导入之前的提取逻辑，如果失败则重新定义
try:
    from save_md_urls import extract_urls_from_text, sanitize_filename
except ImportError:
    import re
    def extract_urls_from_text(text):
        urls = []
        found = re.findall(r'(https?://[^\s<>"`]+)', text)
        for url in found:
            url = url.rstrip('),].;\'')
            if url:
                urls.append(("", url))
        return urls

    def sanitize_filename(name):
        name = re.sub(r'[\\/*?:"<>|]', "_", name)
        name = re.sub(r'[\r\n\t]', "", name)
        return name.strip()

def get_filename_from_url(url):
    parsed = urlparse(url)
    path = parsed.path
    name = os.path.basename(path)
    if not name:
        name = parsed.netloc
    if not name or name == '/':
        name = "index"
    return name

def save_as_webp(page, url, output_dir):
    try:
        # 1. 确定文件名
        filename = sanitize_filename(get_filename_from_url(url))
        if len(filename) > 200:
            filename = filename[:200]
        
        # 2. 检查文件是否已存在
        filepath = os.path.join(output_dir, filename + ".webp")
        counter = 1
        base_path = filepath
        while os.path.exists(filepath):
            filepath = os.path.join(output_dir, f"{filename}_{counter}.webp")
            counter += 1
            
        print(f"正在加载: {url} ...")
        # 3. 访问页面
        # waitUntil='networkidle' 表示等待网络空闲（通常意味着页面加载完毕）
        try:
            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            # 额外等待一小会儿让动态内容加载
            page.wait_for_timeout(2000)
        except Exception as e:
            print(f"⚠ 加载超时或出错，尝试继续截图: {e}")

        # 4. 截图 (PNG 格式)
        print(f"正在截图...")
        png_bytes = page.screenshot(full_page=True, type='png')
        
        # 5. 转换为 WebP
        print(f"正在转换为 WebP...")
        image = Image.open(io.BytesIO(png_bytes))
        image.save(filepath, 'WEBP', quality=80)
        
        print(f"✔ 已保存: {filepath}")
        return True
        
    except Exception as e:
        print(f"✘ 处理失败 {url}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="将网页保存为 WebP 图片")
    parser.add_argument("input", help="包含 URL 的文本文件路径")
    parser.add_argument("--output", "-o", default="downloaded_webps", help="保存图片的文件夹")
    
    args = parser.parse_args()
    
    input_file = args.input
    output_dir = args.output
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")
        
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 '{input_file}' 不存在")
        sys.exit(1)
        
    # 读取 URL
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    links = extract_urls_from_text(content)
    if not links:
        print("未找到链接")
        sys.exit(0)
        
    print(f"找到 {len(links)} 个链接，准备开始截图...")
    
    # 启动 Playwright
    with sync_playwright() as p:
        # 启动 Chromium 浏览器
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 设置视口大小 (宽度设置为常见的桌面宽度，高度会自适应)
        page.set_viewport_size({"width": 1280, "height": 800})
        
        success_count = 0
        seen_urls = set()
        
        for _, url in links:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            if save_as_webp(page, url, output_dir):
                success_count += 1
                
        browser.close()
        
    print(f"\n完成! 成功保存 {success_count} 张 WebP 图片。")
    print(f"文件保存在: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
