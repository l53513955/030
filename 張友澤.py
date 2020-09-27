import requests
from bs4 import BeautifulSoup
import json
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
articles = []  # 目標 全部的文章

def climb(nowurl):
    r = requests.get(nowurl, headers=headers)  # 將網頁資料GET下來
    soup = BeautifulSoup(r.text, "html.parser")  # 將網頁資料以html.parser
    sel = soup.select("div.l-listTable__tr")  # 首頁中的每篇文章的欄位(一行)
    times = len(sel)  # 一頁中要爬幾次
    if nowurl == 'https://www.mobile01.com/topiclist.php?f=740&p=2':  # 如果是爬第二頁 則爬10次就好
        times = 11
    for i in range(1, times):  # 從1開始是因為第0項為分類欄
        url = "https://www.mobile01.com/" + sel[i].a["href"]  # 得到每篇文章的網址 1開始
        newr = requests.get(url, headers=headers)
        newsoup = BeautifulSoup(newr.text, "html.parser")
        title = newsoup.find_all("h1", class_="t2")  # only 0
        title = title[0].text.strip().replace("\n", "")
        text = newsoup.find_all("article")  # 抓內文 0~...
        mainArticle = text[0].text.strip().replace("\n", "")
        date = newsoup.find_all("span", class_="o-fNotes o-fSubMini")  # 日期 0 2 4 6... 人氣:1
        mainArticleDate = date[0].text.strip().replace("\n", "")
        popular = date[1].text.strip().replace("\n", "")
        ID = newsoup.find_all("div", class_="c-authorInfo__id")  # 回覆ID
        author = ID[0].text.strip().replace("\n", "")
        page = newsoup.select("a.c-pagination ")
        comments = [] #一篇文章中全部的留言
        for i in range(1, len(ID)):  # 先把文章第一頁的留言抓下來
            comment = {'ID': ID[i].text.strip().replace("\n", ""), 'time': date[((i+1)*2)].text.strip().replace("\n", ""), 'text': text[i].text.strip().replace("\n", "")}
            comments.append(comment)

        if len(page) != 0:  # 如果流言不只一頁 再抓

            count = 2  # 留言第二頁開始
            page = int(page[len(page)-1].text)  # 總共留言頁數 當作counter
            while page > 1:
                newurl = url
                newurl = url+"&p="+str(count)
                newr = requests.get(newurl, headers=headers)
                newsoup = BeautifulSoup(
                    newr.text, "html.parser")  # 每當讀取新的一頁就重新抓一次回覆數
                text = newsoup.find_all("article")  # 抓內文 0~...
                date = newsoup.find_all("span", class_="o-fNotes o-fSubMini")
                ID = newsoup.find_all("div", class_="c-authorInfo__id")
                for i in range(0, len(ID)):
                    comment = {'ID': ID[i].text.strip().replace("\n", ""), 'time': date[((i+1)*2)].text.strip().replace("\n", ""), 'text': text[i].text.strip().replace("\n", "")}
                    comments.append(comment)  # comments=所有的留言 (該篇文章)

                page = page-1
                count = count+1

        article = {'author': author, 'title': title, 'popular': popular, 'mainArticleDate': mainArticleDate,
                   'mainArticle': mainArticle, 'comments': comments, 'commentAmount': len(comments)}
        # article=一篇文章 articles=全部的文章
        articles.append(article)


climb('https://www.mobile01.com/topiclist.php?f=740')
climb('https://www.mobile01.com/topiclist.php?f=740&p=2')  # 以第二頁的網址帶入
sortedArticles = sorted(
    articles, key=lambda x: x['commentAmount'], reverse=True)  # 按照回覆量排序
with open("成果.json", "w", encoding="utf-8") as f:
    json.dump(sortedArticles, f, indent=4, ensure_ascii=False)  # 以json存入 一開始沒加後面參數都只有英文

print("finifsh")
print(len(sortedArticles))
