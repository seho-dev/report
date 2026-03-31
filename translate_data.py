#!/usr/bin/env python3
"""
日报数据翻译脚本
在生成日报时自动翻译内容
"""

import json
import os
import time
import urllib.request
import urllib.parse

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

def translate(text, target_lang="zh"):
    """调用 MyMemory API 翻译"""
    if not text or len(text.strip()) < 2:
        return text
    
    url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=en|{target_lang}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            if data.get("responseStatus") == 200:
                return data["responseData"]["translatedText"]
    except Exception as e:
        print(f"翻译失败: {e}")
    
    return text

def process_file(filepath):
    """处理单个数据文件"""
    print(f"处理: {filepath}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    modified = False
    
    # GitHub 翻译
    if "github" in data and isinstance(data["github"], list):
        for item in data["github"]:
            if "title_en" not in item:
                item["title_en"] = item.get("title", "")
                item["title"] = translate(item.get("title", ""))
            if "description_en" not in item:
                item["description_en"] = item.get("description", "")
                if item.get("description"):
                    item["description"] = translate(item["description"])
            modified = True
        time.sleep(0.3)
    
    # HN 翻译
    if "hn" in data and isinstance(data["hn"], list):
        for item in data["hn"]:
            if "title_en" not in item:
                item["title_en"] = item.get("title", "")
                item["title"] = translate(item.get("title", ""))
            modified = True
        time.sleep(0.3)
    
    # Twitter 翻译
    if "builders" in data and isinstance(data["builders"], list):
        for item in data["builders"]:
            if "name_en" not in item:
                item["name_en"] = item.get("name", "")
                item["name"] = translate(item.get("name", ""))
            if "bio_en" not in item:
                item["bio_en"] = item.get("bio", "")
                if item.get("bio"):
                    item["bio"] = translate(item["bio"])
            if "tweets" in item and isinstance(item["tweets"], list):
                for tweet in item["tweets"]:
                    if "text_en" not in tweet:
                        tweet["text_en"] = tweet.get("text", "")
                        tweet["text"] = translate(tweet.get("text", ""))
            modified = True
        time.sleep(0.3)
    
    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  已更新: {filepath}")
    
    return modified

def main():
    """主函数"""
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".json")])
    
    print(f"找到 {len(files)} 个数据文件")
    
    for i, filename in enumerate(files):
        filepath = os.path.join(DATA_DIR, filename)
        process_file(filepath)
        
        # 进度提示
        if (i + 1) % 5 == 0:
            print(f"进度: {i + 1}/{len(files)}")
    
    print("完成！")

if __name__ == "__main__":
    main()
