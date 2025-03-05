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

def get_trending_repos(language, datefile):
    HEADERS = {
        'User-Agent'		: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'	: 'gzip,deflate,sdch',
        'Accept-Language'	: 'zh-CN,zh;q=0.8'
    }
    url=f"https://github.com/trending/{language}"
    response=requests.get(url,headers=HEADERS)
    
    # 获取配置中的最大仓库数量
    config = load_config()
    max_repos = config.get("max_repos_per_language", 10)
    
    if response.status_code==200:
        html=response.text
        doc=pq(html)
        items=doc('.Box-row').items()
        count = 0
        for item in items:
            if count >= max_repos:
                break
                
            title=item('.h3').text()
            url=item('.h3').attr('href')
            author=item('.f6').text()
            stars=item('.muted-link').text()
            print(title,url,author,stars)
            with open(datefile,'a',encoding='utf-8') as f:
                f.write(f"{title},{url},{author},{stars}\n")
            count += 1
    else:
        print(f"Failed to retrieve data from {url}")
        
def main():
    # 加载配置
    config = load_config()
    languages = config.get("languages", ["python"])
    
    for language in languages:
        try:
            datefile=f'trending_{language}_{datetime.datetime.now().strftime("%Y-%m-%d")}.csv'
            get_trending_repos(language, datefile)
            print(f"成功抓取 {language} 语言的trending项目")
        except Exception as e:
            print(f"抓取 {language} 语言时出错: {e}")
    
if __name__=='__main__':
    main()
        
            

    
