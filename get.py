
import datetime
import codecs
import requests
import os
import time
from pyquery import PyQuery as pq

def get_trending_repos(language,datefile):
    HEADERS = {
        'User-Agent'		: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'	: 'gzip,deflate,sdch',
        'Accept-Language'	: 'zh-CN,zh;q=0.8'
    }
    url=f"https://github.com/trending/{language}"
    response=requests.get(url,headers=HEADERS)
    if response.status_code==200:
        html=response.text
        doc=pq(html)
        items=doc('.Box-row').items()
        for item in items:
            title=item('.h3').text()
            url=item('.h3').attr('href')
            author=item('.f6').text()
            stars=item('.muted-link').text()
            print(title,url,author,stars)
            with open(datefile,'a',encoding='utf-8') as f:
                f.write(f"{title},{url},{author},{stars}\n")
    else:
        print(f"Failed to retrieve data from {url}")
        
def main():
    language='python'
    datefile=f'trending_{language}_{datetime.datetime.now().strftime("%Y-%m-%d")}.csv'
    get_trending_repos(language,datefile)
    
if __name__=='__main__':
    main()
        
            

    
