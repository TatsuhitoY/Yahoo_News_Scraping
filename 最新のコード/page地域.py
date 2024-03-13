import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import csv
import datetime
import numpy as np

############################################################################################################################

def job_main():
    tz = datetime.timezone(datetime.timedelta(hours=9))
    a = datetime.datetime.now(tz)
    t_2 = a.strftime('%m-%d')
    file_name = '/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/データファイル/地域 {}.csv'.format(t_2)
    news_page_num = 0 #この変数は記事を選ぶページを巡回する
    while True: #while文の最初の階層でcontinueが適用されると記事の情報が取得されず最後のprint文も機能せず、そのままスキップされる
        news_page_num += 1
        df = pd.DataFrame(index=[], columns=['text', 'media', 'cmt', 'p_time', 's_time', 'link', 'content'])
        URL = "https://news.yahoo.co.jp/topics/local?page={}".format(news_page_num)
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
          #ここでは記事全文を読むというリンクをクリックする前の記事の仮表示ページでスクレイピングしている
          rest = requests.get(url)
          soup = BeautifulSoup(rest.text, "html.parser")
          #title取得
          title = soup.find(class_ = "sc-bIZIuE ifDJGS")
          if title:
            title_name = title.text
          else:
            title_name = "不明"

          #media取得
          media = soup.find(class_ = "sc-cMSbJT jievlP")#主要トピックの記事
          if not media:
              #サッカー速報などで、画像の上にしかメディアが掲載されていない時
              media = soup.find(class_ = "sc-kCAfiB eCymsD")
          if media:
            media_name = media.text
          else:
            media_name = "不明"

          #p_time取得
          #通常の記事で、画像の上に表示されている
          p_time = soup.find(class_ = "sc-ivQgGC knlTXj")
          if not p_time:
            #動画の記事
            p_time = soup.find(class_ = "sc-iBZwnA efNSfe")
          if not p_time:
            #画像と動画の無い記事
            p_time = soup.find(class_ = "sc-kYWsKJ hjcZTo")
          if p_time:
            release_time = p_time.text
          else:
            release_time = "不明"

          #HTMLタグは一つ上の階層、つまりriff-text-currentの一個上の階層 その階層の時は、<svg>で閉じているから数字はその範囲外にある
          #コメントの数が多くて表示が赤色になっている時
          cmt_num = soup.find(class_ = "sc-likbZx gaaRWd")
          if not cmt_num:
              #コメントの数が少なくて表示が赤色になっている時セカンド
              cmt_num = soup.find(class_ = "sc-guHSqG htCtaI")
          if not cmt_num:
              #コメントの数が少なくて表示が青色になっている時
              cmt_num = soup.find(class_ = "sc-guHSqG bxupay")
          if cmt_num:
            c_num = int(cmt_num.text)
          else:
            c_num = 0

          #目的のhrefが含まれている階層のclassを取得する。
          url_text = soup.find(class_ = "sc-gITAse fNjniK")
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
          print("記事の番号 -> {0} \n\ntitle:{1}\nmedia:{2} comment number:{3}, post time:{4}, scrape_time:{5} url:{6} \ncontent:{7}".format(num, title_name, media_name, c_num, release_time, t, url, content_final))
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
