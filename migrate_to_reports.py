#!/usr/bin/env python3
"""
迁移旧格式 JSON 到新的 reports 格式
保留所有原始字段，只是重组结构
"""

import json
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__)) + "/data"

def migrate_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 如果已经是 reports 格式，跳过
    if "reports" in data:
        print(f"  已是新格式: {os.path.basename(filepath)}")
        return False
    
    reports = []
    
    # GitHub
    if "github" in data and isinstance(data["github"], list):
        for item in data["github"]:
            reports.append({
                "id": item.get("id", ""),
                "type": "github",
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "summary": item.get("description", ""),
                "content": item.get("description", ""),
                # 保留所有原始字段
                "language": item.get("language"),
                "stars": item.get("stars"),
                "starsToday": item.get("starsToday"),
                "description": item.get("description"),
                "description_en": item.get("description_en"),
                "title_en": item.get("title_en"),
                # 原始数据保留
                "_raw": item,
            })
    
    # HN
    if "hn" in data and isinstance(data["hn"], list):
        for item in data["hn"]:
            reports.append({
                "id": item.get("id", ""),
                "type": "hn",
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "summary": "",
                "content": "",
                # 保留所有原始字段
                "points": item.get("points"),
                "comments": item.get("comments"),
                "title_en": item.get("title_en"),
                "_raw": item,
            })
    
    # Builders (AI Twitter)
    if "builders" in data and isinstance(data["builders"], list):
        for item in data["builders"]:
            reports.append({
                "id": item.get("id", ""),
                "type": "ai",
                "title": item.get("name", ""),
                "url": f"https://x.com/{item.get('handle', '')}",
                "summary": item.get("bio", ""),
                "content": "",
                # 保留所有原始字段
                "source": item.get("source"),
                "name": item.get("name"),
                "name_en": item.get("name_en"),
                "handle": item.get("handle"),
                "bio": item.get("bio"),
                "bio_en": item.get("bio_en"),
                "tweets": item.get("tweets", []),
                "_raw": item,
            })
    
    # 构建新格式
    new_data = {
        "date": data.get("date", os.path.basename(filepath).replace(".json", "")),
        "reports": reports
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    
    print(f"  迁移完成: {os.path.basename(filepath)} -> {len(reports)} 条报告")
    return True

def main():
    files = sorted([
        f for f in os.listdir(DATA_DIR) 
        if f.endswith(".json") and not f.startswith("digest") and not f.startswith("tech-report")
    ])
    
    print(f"找到 {len(files)} 个数据文件，开始迁移...")
    migrated = 0
    for filename in files:
        filepath = os.path.join(DATA_DIR, filename)
        if migrate_file(filepath):
            migrated += 1
    
    print(f"\n完成！共迁移 {migrated} 个文件")

if __name__ == "__main__":
    main()
