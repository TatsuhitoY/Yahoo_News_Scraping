import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import csv
import datetime
import numpy as np

############################################################################################################################
def job_main():
    category_list = ["https://news.yahoo.co.jp/topics/top-picks?page={}", "https://news.yahoo.co.jp/topics/domestic?page={}", "https://news.yahoo.co.jp/topics/world?page={}", "https://news.yahoo.co.jp/topics/local?page={}", "https://news.yahoo.co.jp/topics/science?page={}", "https://news.yahoo.co.jp/topics/business?page={}", "https://news.yahoo.co.jp/topics/it?page={}", "https://news.yahoo.co.jp/topics/entertainment?page={}", "https://news.yahoo.co.jp/topics/sports?page={}"]
    category_file_list = ['/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/データファイル/主要 {}.csv', '/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/データファイル/国内 {}.csv', '/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/データファイル/国際 {}.csv', '/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/データファイル/地域 {}.csv', '/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/データファイル/科学 {}.csv', '/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/データファイル/経済 {}.csv', '/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/データファイル/IT {}.csv', '/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/データファイル/エンタメ {}.csv', '/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/データファイル/スポーツ {}.csv']
    category_inform_list = ["主要 1/9", "国内 2/9", '国際 3/9', '地域 4/9', '科学 5/9', '経済 6/9', 'IT 7/9', 'エンタメ 8/9', 'スポーツ 9/9']
    for i in range(len(category_list)):
        tz = datetime.timezone(datetime.timedelta(hours=9))
        a = datetime.datetime.now(tz)
        t_2 = a.strftime('%m-%d')
        file_name_n = category_file_list[i]
        file_name = file_name_n.format(t_2)
        inform = category_inform_list[i]
        news_page_num = 0 #この変数は記事を選ぶページを巡回する
        URL_n = category_list[i]
        while True: #while文の最初の階層でcontinueが適用されると記事の情報が取得されず最後のprint文も機能せず、そのままスキップされる
            news_page_num += 1
            df = pd.DataFrame(index=[], columns=['text', 'media', 'cmt', 'p_time', 's_time', 'link', 'content'])
            URL = URL_n.format(news_page_num)
            rest = requests.get(URL)
            if not rest:
                break
            print("\n#####################################################")
            print(f"ページ番号 -> {news_page_num}")

            soup = BeautifulSoup(rest.text, "html.parser")
            data_list = soup.find_all(href=re.compile("news.yahoo.co.jp/pickup/"))
            #article_listにはサイトのそのページにおける複数の記事のurlを格納する
            article_list = [data.attrs["href"] for data in data_list if "_cl_vmodule:st_topics" in data.attrs["data-cl-params"]]
            # print([[v, i] for v, i in enumerate(article_list)])
            for num, url in enumerate(article_list):
              rest = requests.get(url)
              soup = BeautifulSoup(rest.text, "html.parser")
              #title取得
              title = soup.find(class_ = "sc-eWDEPs cZtZIe")
              if title:
                title_name = title.text
              else:
                title_name = "不明"

              #media取得
              media = soup.find(class_ = "sc-hViAGI idupYh")#主要トピックの記事
              if media:
                media_name = media.text
              else:
                media_name = "不明"

              #p_time取得
              p_time = soup.find(class_ = "sc-cbcvrX ckoxeS")
              if not p_time:
                p_time = soup.find(class_ = "sc-imYgaF gmmNuR")
              if not p_time:
                p_time = soup.find(class_ = "sc-koJQpy cvByip")
              if p_time:
                release_time = p_time.text
              else:
                release_time = "不明"

              cmt_num = soup.find(class_ = "sc-eYBPub fKfcWj")
              if not cmt_num:
                cmt_num = soup.find(class_ = 'sc-bJazwb gtPmGv riff-text-current')
              if cmt_num:
                c_num = int(cmt_num.text)
              else:
                c_num = 0

              url_text = soup.find(class_ = "sc-jDrVcX iQlnEi")
              url_text = url_text.attrs['href']
              content_final = ""

              content_top = soup.find(class_ = "sc-lSeQO gDJTCh highLightSearchTarget")

              #記事の各ページの内容を取得
              article_page_num = 0
              while True:
                  article_page_num += 1
                  content_add = ""
                  url_range = url_text + f"?page={article_page_num}"
                  rest = requests.get(url_range)
                  if rest.status_code == 404:
                    break
                  soup = BeautifulSoup(rest.text, "html.parser")
                  content_list = soup.find_all(class_ = "sc-fcdeBU fwtBPB")
                  if not content_list:
                      content_list = soup.find_all(class_ = "sc-jtggT bAhgUU yjSlinkDirectlink highLightSearchTarget")
                  if not content_list:
                      content_list = soup.find_all(class_ = "articleBody")
                  if not content_list:
                      content_list = soup.find_all(class_ = "article_body highLightSearchTarget")
                  if content_list:
                      for i in content_list: #content_listはlistのように扱う
                          content_add += i.text
                  else:
                      if content_top:
                          content_add = content_top.text
                          content_list = [content_top]
                      else:
                          break
                  #どんな数字を代入しても最初の記事を表示するurlが存在するので、内容が重複したらbreakする
                  if content_list[0].text in content_final:
                      break

                  content_final += content_add


              tz = datetime.timezone(datetime.timedelta(hours=9))
              a = datetime.datetime.now(tz)
              t = a.strftime('%Y%m%d%H%M%S')
              print("\n----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
              print(f"記事の番号 -> {num}          {inform}\n\ntitle:{title_name}\nmedia:{media_name} comment number:{c_num}, post time:{release_time}, scrape_time:{t} url:{url} \ncontent:{content_final}")
              df_add = pd.DataFrame(data = np.array([[title_name, media_name, c_num, release_time, t,  url, content_final]]), index=[0], columns=['text', 'media', 'cmt', 'p_time', 's_time', 'link', 'content'])
              df = pd.concat([df, df_add])

            if news_page_num == 1:
                df.to_csv(file_name, index = False)
            else:
                with open(file_name, 'a') as f:
                    writer = csv.writer(f, lineterminator='\n')
                    for ary in df.values:
                        writer.writerow(ary)

job_main()
