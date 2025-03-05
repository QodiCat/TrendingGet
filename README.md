# GitHub Trending 项目抓取工具

帮我整理github最新有趣的项目的小助手
可以爬取github的trending项目，并保存到本地
可以生成日期文件夹，下面有markdown文档
可以根据我设置的偏好，去针对性爬取我的内容

## 配置说明

项目使用 `config.json` 文件进行配置，支持以下选项：

```json
{
  "languages": [
    "python",
    "javascript",
    "go",
    "java",
    "rust"
  ],
  "auto_push": true,
  "update_frequency": "daily",
  "max_repos_per_language": 10,
  "file_format": "markdown"
}
```

### 配置项说明

- `languages`: 要抓取的编程语言列表，可以添加或删除语言
- `auto_push`: 是否自动提交并推送到Git仓库
- `update_frequency`: 更新频率（目前仅支持daily）
- `max_repos_per_language`: 每种语言最多抓取的仓库数量
- `file_format`: 输出文件格式（目前仅支持markdown）

## 使用方法

1. 编辑 `config.json` 文件，设置你想要抓取的编程语言
2. 运行 `python check.py` 抓取trending项目并生成markdown文件
3. 或者运行 `python get.py` 抓取trending项目并生成CSV文件

