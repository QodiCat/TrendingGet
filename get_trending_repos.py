# coding:utf-8

import datetime
import codecs
import requests
import os
import time
import json
from pyquery import PyQuery as pq
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from secret import email_password
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
            "file_format": "markdown",
            "email": {
                "enable": False,
                "sender": "",
                "password": "",
                "receiver": "",
                "smtp_server": "",
                "smtp_port": 465
            }
        }

def git_add_commit_push(date, filename):
    cmd_git_add = 'git add {filename}'.format(filename=filename)
    cmd_git_commit = 'git commit -m "{date}"'.format(date=date)
    cmd_git_push = 'git push -u origin main'

    os.system(cmd_git_add)
    os.system(cmd_git_commit)
    os.system(cmd_git_push)


def create_markdown(date, filename):
    if os.path.exists(filename):
        pass
    else:
        with open(filename, 'w') as f:
            f.write("# " + date + "\n")

def send_email(date, filename):
    """
    发送邮件功能
    :param date: 日期
    :param filename: 文件名
    :return: 是否发送成功
    """
    # 读取配置
    config = load_config()
    email_config = config.get("email", {})
    
    # 检查是否启用邮件功能
    if not email_config.get("enable", False):
        print("邮件发送功能未启用")
        return False
    
    # 获取邮件配置
    sender = email_config.get("sender", "")
    password = email_password
    receiver = email_config.get("receiver", "")
    smtp_server = email_config.get("smtp_server", "")
    smtp_port = email_config.get("smtp_port", 465)
    
    # 检查配置是否完整
    if not all([sender, password, receiver, smtp_server]):
        print("邮件配置不完整，无法发送邮件")
        return False
    
    try:
        # 读取文件内容
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建邮件对象
        message = MIMEMultipart()
        message['From'] = sender  # 简化From头部，只使用邮箱地址
        message['To'] = receiver
        subject = f'GitHub Trending 日报 ({date})'
        message['Subject'] = Header(subject, 'utf-8')
        
        # 添加邮件正文
        message.attach(MIMEText(content, 'markdown', 'utf-8'))
        
        # 发送邮件
        if smtp_port == 465:
            # SSL连接
            smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            # 普通连接
            smtp = smtplib.SMTP(smtp_server, smtp_port)
            smtp.starttls()  # 启用TLS加密
            
        smtp.login(sender, password)
        smtp.sendmail(sender, receiver, message.as_string())
        smtp.quit()
        
        print(f"邮件已成功发送到 {receiver}")
        return True
    except Exception as e:
        print(f"发送邮件时出错: {e}")
        return False


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
        
        for project in sorted_projects:
            f.write(u"* [{title}]({url}) ⭐{stars} - {description}\n".format(
                title=project['title'], 
                url=project['url'], 
                stars=project['stars_text'], 
                description=project['description']
            ))


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
    start()
