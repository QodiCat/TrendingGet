# coding:utf-8

import datetime
import codecs
import requests
import os
from pyquery import PyQuery as pq
from dotenv import load_dotenv
from utils.config import load_config
from utils.gitpush import git_add_commit_push
from utils.emails import send_email
from ai import ai_response
def create_markdown(date, filename):
    if os.path.exists(filename):
        pass
    else:
        with open(filename, 'w') as f:
            f.write("# " + date + "\n")


def get_trending_repos(language, filename):
    HEADERS = {
        'User-Agent'		: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'	: 'gzip,deflate,sdch',
        'Accept-Language'	: 'zh-CN,zh;q=0.8'
    }
        # 获取配置中的最大仓库数量
    config = load_config()
    max_repos = config.get("max_repos_per_language", 10)
    proxies = config.get("proxy", {})
    
    url = 'https://github.com/trending/{language}'.format(language=language)
    r = requests.get(url, headers=HEADERS,proxies=proxies)
    assert r.status_code == 200
    
    d = pq(r.content)
    items = d('div.Box article.Box-row')



    # 收集所有项目信息
    projects = []
    
    for item in items:
        i = pq(item)
        title = i(".lh-condensed a").text()
        owner = i(".lh-condensed span.text-normal").text()
        description = i("p.col-9").text()
        url = i(".lh-condensed a").attr("href")
        url = "https://github.com" + url
        
        # 获取 Star 数量
        stars_element = i("span.d-inline-block.float-sm-right")
        if stars_element:
            stars_text = stars_element.text().strip()
        else:
            # 尝试其他可能的选择器
            stars_element = i("span.float-right")
            if stars_element:
                stars_text = stars_element.text().strip()
            else:
                # 如果找不到 Star 数，使用备用方法
                stars_text = i("a.Link--muted.d-inline-block.mr-3").text().strip()
                
        # 清理 Star 文本，只保留数字
        if stars_text:
            # 提取数字部分
            import re
            stars_match = re.search(r'([\d,]+)\s*stars', stars_text, re.IGNORECASE)
            if stars_match:
                stars_text = stars_match.group(1)
            
            # 移除逗号，转换为整数
            try:
                stars_count = int(stars_text.replace(',', ''))
            except (ValueError, AttributeError):
                # 如果无法转换为整数，使用0
                stars_count = 0
        else:
            stars_count = 0
            stars_text = "未知"
        
        projects.append({
            'title': title,
            'url': url,
            'description': description,
            'stars_count': stars_count,
            'stars_text': stars_text
        })
    
    # 按照 Star 数排序（降序）
    sorted_projects = sorted(projects, key=lambda x: x['stars_count'], reverse=True)
    
    # 限制项目数量
    sorted_projects = sorted_projects[:max_repos]
    
    # 写入文件
    with codecs.open(filename, "a", "utf-8") as f:
        f.write('\n## {language}\n'.format(language=language))
        f.write('\n')  # 添加空行，使格式更规范
        
        for project in sorted_projects:
            # 确保描述不为空
            original_description = project['description'] if project['description'] else "无描述"
            
            # 使用AI翻译描述并解释困难概念
            if original_description != "无描述":
                prompt = f"这是一个github的description，翻译成中文，注意对于某些专有名词要保留\n\n{original_description}"
                ai_description = ai_response(prompt)
                description = ai_description
            else:
                description = original_description
            
            # 格式化输出，使其更加规范
            f.write(u"* [{title}]({url}) ⭐ {stars}\n".format(
                title=project['title'], 
                url=project['url'], 
                stars=project['stars_text']
            ))
            f.write(u"  {original_description}\n".format(
                original_description=original_description
            ))
            
            # 添加AI翻译和解释，使用缩进使其更易读
            if description != original_description:
                # 分割AI回复的多行内容并保持格式
                ai_lines = description.strip().split('\n')
                for line in ai_lines:
                    f.write(u"    {line}\n".format(line=line))
            
            # 添加空行，使不同项目之间有更好的视觉分隔
            f.write(u"\n")


def start():
    # 加载配置
    config = load_config()
    languages = config.get("languages", ["python"])
    auto_push = config.get("auto_push", True)
    
    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = 'repos_data/{date}.md'.format(date=strdate)

    # create markdown file
    create_markdown(strdate, filename)

    # 遍历配置的所有语言进行抓取
    for language in languages:
        try:
            get_trending_repos(language, filename)
            print(f"成功抓取 {language} 语言的trending项目")
        except Exception as e:
            print(f"抓取 {language} 语言时出错: {e}")

    # 发送邮件
    email_config = config.get("email", {})
    if email_config.get("enable", False):
        send_email(strdate, filename)
    
    #git add commit push
    if auto_push:
        git_add_commit_push(strdate, filename)
        print(f"已自动提交并推送到Git仓库")
    else:
        print(f"已生成文件 {filename}，但未推送到Git仓库")


if __name__ == '__main__':
    load_dotenv()
    start()
