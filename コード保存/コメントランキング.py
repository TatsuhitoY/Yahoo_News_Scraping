from janome.tokenizer import Tokenizer
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import csv
import datetime

############################################################################################################################

np_dic = {}
fp = open("pn.csv", "rt", encoding="utf-8")
reader = csv.reader(fp, delimiter='\t')
for i, row in enumerate(reader):
  name = row[0]
  result = row[1]
  np_dic[name] = result #np_dicという辞書に格納している

############################################################################################################################

def judge_pne(text):
  tok = Tokenizer()
  res = {"p":0, "n":0, "e":0}
  for t in tok.tokenize(text):
    bf = t.base_form # 基本形
    if bf in np_dic:
      r = np_dic[bf]
      if r in res:
        res[r] += 1
  cnt = res["p"] + res["n"] + res["e"]
  print(res)
  print("ポジティブ度", res["p"] / cnt)
  print("ネガティブ度", res["n"] / cnt)

############################################################################################################################

df = pd.DataFrame(index=[], columns=['text', 'cmt', 'time', 'link'])

URL = "https://news.yahoo.co.jp/ranking/comment"
rest = requests.get(URL)
soup = BeautifulSoup(rest.text, "html.parser")
data_list = soup.find_all(href=re.compile("news.yahoo.co.jp/articles"))
article_list = [data.attrs["href"] for data in data_list if "_cl_vmodule:ranking" in data.attrs["data-cl-params"]]
for num, url in enumerate(article_list):
  rest = requests.get(url)
  soup = BeautifulSoup(rest.text, "html.parser")
  title = soup.find(class_ = "sc-gpHHfC fBLSKY")
  cmt_num = soup.find(class_ = "sc-likbZx gaaRWd")
  p_time = soup.find(class_ = "sc-kQsIoO eQNumw")
  if cmt_num is not None:
    c_num = int(cmt_num.text)
  else:
    cmt_num = soup.find(class_ = "sc-likbZx gmKLBV")
    if cmt_num is not None:
      c_num = int(cmt_num.text)
    else:
      c_num = 0
  print("\n {0} title:{1}\n comment number:{2}, post time:{3}, url:{4} ".format(num, title.text, c_num, p_time.text, url), end = "")
  df = df.append(pd.Series([title.text, c_num, p_time.text,  url], index=df.columns), ignore_index=True)

############################################################################################################################

tz = datetime.timezone(datetime.timedelta(hours=9))
a = datetime.datetime.now(tz)
b = str(a.date())[5:] + "," + str(a.time())[:5]
df.to_csv('/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/csv コメントランキング/コメント{}.csv'.format(b), index = False)
