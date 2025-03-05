# coding:utf-8

import datetime
import codecs
import requests
import os
import time
import json
from pyquery import PyQuery as pq

# 读取配置文件
def load_config():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        # 返回默认配置
        return {
            "languages": ["python"],
            "auto_push": True,
            "update_frequency": "daily",
            "max_repos_per_language": 10,
            "file_format": "markdown"
        }

def git_add_commit_push(date, filename):
    cmd_git_add = 'git add {filename}'.format(filename=filename)
    cmd_git_commit = 'git commit -m "{date}"'.format(date=date)
    cmd_git_push = 'git push -u origin master'

    os.system(cmd_git_add)
    os.system(cmd_git_commit)
    os.system(cmd_git_push)


def createMarkdown(date, filename):
    if os.path.exists(filename):
        pass
    else:
        with open(filename, 'w') as f:
            f.write("## " + date + "\n")


def scrape(language, filename):
    HEADERS = {
        'User-Agent'		: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'	: 'gzip,deflate,sdch',
        'Accept-Language'	: 'zh-CN,zh;q=0.8'
    }

    url = 'https://github.com/trending/{language}'.format(language=language)
    r = requests.get(url, headers=HEADERS)
    assert r.status_code == 200
    
    d = pq(r.content)
    items = d('div.Box article.Box-row')

    # 获取配置中的最大仓库数量
    config = load_config()
    max_repos = config.get("max_repos_per_language", 10)

    # codecs to solve the problem utf-8 codec like chinese
    with codecs.open(filename, "a", "utf-8") as f:
        f.write('\n#### {language}\n'.format(language=language))

        for i, item in enumerate(items):
            if i >= max_repos:
                break
                
            i = pq(item)
            title = i(".lh-condensed a").text()
            owner = i(".lh-condensed span.text-normal").text()
            description = i("p.col-9").text()
            url = i(".lh-condensed a").attr("href")

            f.write(u"* [{title}]({url}):{description}\n".format(title=title, url=url, description=description))


def job():
    # 加载配置
    config = load_config()
    languages = config.get("languages", ["python"])
    auto_push = config.get("auto_push", True)
    
    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = '{date}.md'.format(date=strdate)

    # create markdown file
    createMarkdown(strdate, filename)

    # 遍历配置的所有语言进行抓取
    for language in languages:
        try:
            scrape(language, filename)
            print(f"成功抓取 {language} 语言的trending项目")
        except Exception as e:
            print(f"抓取 {language} 语言时出错: {e}")

    # git add commit push
    if auto_push:
        git_add_commit_push(strdate, filename)
        print(f"已自动提交并推送到Git仓库")
    else:
        print(f"已生成文件 {filename}，但未推送到Git仓库")


if __name__ == '__main__':
    job()
