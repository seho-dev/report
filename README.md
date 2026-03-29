# 技术日报 Daily Tech Report

每日技术资讯精选，聚合 GitHub Trending、Hacker News、AI Twitter 热门内容。

## 在线访问

- **地址**: https://report.yinzhuoei.com
- **GitHub Pages**: https://seho-dev.github.io/report

## 功能特性

- 📱 响应式设计，支持手机和桌面
- 🔄 Tab 切换：GitHub / Hacker News / AI Twitter
- 📅 按日期分组展示，每页 10 天
- 🔍 展开/收起详情，完整 Markdown 渲染
- 🔗 原文链接直达

## 数据格式

```json
{
  "date": "2026-03-29",
  "reports": [
    {
      "id": "github-2026-03-29-01",
      "type": "github",
      "title": "GitHub Trending Top 10 - 2026-03-29",
      "url": "https://github.com/trending",
      "summary": "今日热门摘要",
      "content": "完整的 Markdown 内容..."
    }
  ]
}
```

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| date | string | 日期 YYYY-MM-DD |
| reports | array | 报告列表 |
| type | string | github / hn / twitter |
| title | string | 标题 |
| url | string | 原文链接 |
| summary | string | 摘要 |
| content | string | 完整 Markdown 内容 |

## 本地开发

```bash
# 进入目录
cd ~/daily-report

# 启动本地服务器
python -m http.server 8080

# 访问 http://localhost:8080
```

## 自动部署

定时任务每天 8:00 自动抓取数据并推送到 GitHub。

## 文件结构

```
daily-report/
├── index.html      # 前端页面
├── data/          # JSON 数据文件
│   ├── 2026-03-29.json
│   └── ...
├── CNAME          # 自定义域名配置
└── README.md
```

## 技术栈

- 纯 HTML/CSS/JavaScript
- Marked.js for Markdown 渲染
- highlight.js for 代码高亮
- Google Fonts (Noto Serif SC, DM Sans)

## License

MIT
