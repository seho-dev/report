#!/usr/bin/env python3
"""
日报数据翻译脚本 - LLM版本
支持 reports 数组格式，含 type 字段
"""

import json
import os
import sys
import time
import anthropic

# 配置
DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"
MODEL = "claude-sonnet-4-20250514"
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
USE_ANTHROPIC = bool(ANTHROPIC_API_KEY)

def translate_with_claude(texts, target_lang="Chinese"):
    """使用 Claude 翻译"""
    if not texts or all(not t or not t.strip() for t in texts):
        return texts
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # 过滤空文本
    valid_texts = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
    if not valid_texts:
        return texts
    
    texts_to_translate = [t for _, t in valid_texts]
    
    prompt = f"""Translate the following English texts to {target_lang}. 
For each item, provide the translation on a new line, keeping the same order.
Only output the translations, one per line, nothing else.

Texts to translate:
{chr(10).join([f"{i+1}. {t}" for i, t in enumerate(texts_to_translate)])}
"""
    
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    
    translations = response.content[0].text.strip().split('\n')
    translations = [t.split('. ', 1)[-1].strip() if '. ' in t else t.strip() for t in translations]
    
    # 重建完整结果（保留原位置）
    result = texts.copy()
    for idx, trans in zip([i for i, _ in valid_texts], translations):
        result[idx] = trans
    
    return result

def translate_batch(texts, batch_size=10):
    """批量翻译"""
    if not texts or all(not t or not t.strip() for t in texts):
        return texts
    
    all_translations = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        print(f"  翻译进度: {min(i+batch_size, len(texts))}/{len(texts)}")
        
        try:
            if USE_ANTHROPIC:
                translations = translate_with_claude(batch)
            else:
                print("  请设置 ANTHROPIC_API_KEY 环境变量")
                return texts
            
            all_translations.extend(translations)
            time.sleep(1)
            
        except Exception as e:
            print(f"  翻译失败: {e}")
            all_translations.extend(batch)
    
    return all_translations

def process_file(filepath):
    """处理单个数据文件"""
    print(f"处理: {filepath}")
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    modified = False
    
    # 新格式: reports 数组
    if "reports" in data and isinstance(data["reports"], list):
        for item in data["reports"]:
            item_type = item.get("type", "github")
            
            # GitHub: 翻译 title 和 description
            if item_type == "github":
                if "title_en" not in item:
                    item["title_en"] = item.get("title", "")
                if item.get("title_en") and (not item.get("title") or item.get("title") == item.get("title_en")):
                    titles = translate_batch([item["title_en"]])
                    if titles:
                        item["title"] = titles[0]
                        modified = True
                
                if "description_en" not in item:
                    item["description_en"] = item.get("description", "")
                if item.get("description_en"):
                    descs = translate_batch([item["description_en"]])
                    if descs:
                        item["description"] = descs[0]
                        modified = True
                time.sleep(0.5)
            
            # HN: 翻译 title
            elif item_type == "hn":
                if "title_en" not in item:
                    item["title_en"] = item.get("title", "")
                if item.get("title_en"):
                    titles = translate_batch([item["title_en"]])
                    if titles:
                        item["title"] = titles[0]
                        modified = True
                time.sleep(0.5)
            
            # AI (summary)
            elif item_type == "ai":
                if "summary_en" not in item:
                    item["summary_en"] = item.get("summary", "")
                if item.get("summary_en"):
                    summaries = translate_batch([item["summary_en"]])
                    if summaries:
                        item["summary"] = summaries[0]
                        modified = True
                time.sleep(0.5)
        
        # Twitter: 翻译 handle, name, bio, tweets
        # 注意: twitter 类型在 reports 里可能叫 twitter 或保持原样
        twitter_items = [r for r in data["reports"] if r.get("type") == "twitter"]
        for item in twitter_items:
            if "name_en" not in item and item.get("name"):
                item["name_en"] = item["name"]
            
            if item.get("bio_en") and item.get("bio") == item.get("bio_en"):
                bios = translate_batch([item["bio_en"]])
                if bios:
                    item["bio"] = bios[0]
                    modified = True
            
            if "tweets" in item and isinstance(item["tweets"], list):
                for tweet in item["tweets"]:
                    if "text_en" not in tweet:
                        tweet["text_en"] = tweet.get("text", "")
                    if tweet.get("text_en"):
                        tweets_trans = translate_batch([tweet["text_en"]])
                        if tweets_trans:
                            tweet["text"] = tweets_trans[0]
                            modified = True
            time.sleep(0.5)
    
    # 旧格式兼容: github/hn/builders 字段
    else:
        if "github" in data and isinstance(data["github"], list):
            for item in data["github"]:
                if "title_en" not in item:
                    item["title_en"] = item.get("title", "")
                    item["description_en"] = item.get("description", "")
                    if item.get("description_en"):
                        descs = translate_batch([item["description_en"]])
                        if descs:
                            item["description"] = descs[0]
                    modified = True
                    time.sleep(0.5)
            
            # 翻译标题
            titles = [item.get("title_en", item.get("title", "")) for item in data["github"]]
            translations = translate_batch(titles)
            for item, trans in zip(data["github"], translations):
                item["title"] = trans
            modified = True
        
        if "hn" in data and isinstance(data["hn"], list):
            titles = []
            for item in data["hn"]:
                if "title_en" not in item:
                    item["title_en"] = item.get("title", "")
                titles.append(item["title_en"])
            
            if titles:
                translations = translate_batch(titles)
                for item, trans in zip(data["hn"], translations):
                    item["title"] = trans
                modified = True
                time.sleep(0.5)
        
        if "builders" in data and isinstance(data["builders"], list):
            for item in data["builders"]:
                if "name_en" not in item:
                    item["name_en"] = item.get("name", "")
                    item["bio_en"] = item.get("bio", "")
                
                if item.get("bio_en"):
                    bios = translate_batch([item["bio_en"]])
                    if bios:
                        item["bio"] = bios[0]
                        modified = True
                
                if "tweets" in item and isinstance(item["tweets"], list):
                    for tweet in item["tweets"]:
                        if "text_en" not in tweet:
                            tweet["text_en"] = tweet.get("text", "")
                        if tweet.get("text_en"):
                            tweets_trans = translate_batch([tweet["text_en"]])
                            if tweets_trans:
                                tweet["text"] = tweets_trans[0]
                                modified = True
                time.sleep(0.5)
    
    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  已更新: {filepath}")
    
    return modified

def main():
    if not ANTHROPIC_API_KEY:
        print("错误: 请设置 ANTHROPIC_API_KEY 环境变量")
        print("  export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)
    
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".json") and not f.startswith("digest") and not f.startswith("tech-report")])
    
    print(f"使用 Claude 翻译")
    print(f"找到 {len(files)} 个数据文件")
    
    for i, filename in enumerate(files):
        filepath = os.path.join(DATA_DIR, filename)
        process_file(filepath)
        print(f"进度: {i + 1}/{len(files)}")
    
    print("完成！")

if __name__ == "__main__":
    main()
