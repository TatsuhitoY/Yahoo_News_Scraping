def job_main():
    print("job_main")
    df = pd.DataFrame(index=[], columns=['text', 'media', 'cmt', 'p_time', 's_time', 'link'])
    URL = "https://news.yahoo.co.jp/"
    rest = requests.get(URL)
    soup = BeautifulSoup(rest.text, "html.parser")
    data_list = soup.find_all(href=re.compile("news.yahoo.co.jp/pickup"))

    article_list = [data.attrs["href"] for data in data_list if "_cl_vmodule:tpc_maj;_cl_link:title;_cl_position" in data.attrs["data-cl-params"]]
    for num, url in enumerate(article_list):
      rest = requests.get(url)
      soup = BeautifulSoup(rest.text, "html.parser")
      title = soup.find(class_ = "sc-fbSTYX itBHqi")
      if title is not None:
        title_name = title.text
      else:
        title = soup.find(class_ = "sc-gpHHfC fBLSKY")
        if title is not None:
          title_name = title.text
        else:
          title_name = "不明"

      media = soup.find(class_ = "sc-dwIOUI bHRjIw")#主要トピックの記事
      if media is not None:
        media_name = media.text
      else:
        media = soup.find(class_ = "sc-jeCdPy isJHzE")
        if media is not None:
          media_name = media.text
        else:
          media_name = "不明"

      p_time = soup.find(class_ = "sc-gyFTku bAFXNI")
      if p_time is not None:
        release_time = p_time.text
      else:
        p_time = soup.find(class_ = "sc-fXNpEn dCYdPS") #動画が掲載されている場合
        if p_time is not None:
          release_time = p_time.text
        else:
          p_time = soup.find(class_ = "sc-lmuQER iPpQvk") #記事画像がない場合
          if p_time is not None:
            release_time = p_time.text
          else:
            release_time = "不明"

      cmt_num = soup.find(class_ = "sc-blJnwB gHcNtW")
      if cmt_num is not None:
        c_num = int(cmt_num.text)
      else:
        cmt_num = soup.find(class_ = "sc-likbZx gmKLBV")
        if cmt_num is not None:
          c_num = int(cmt_num.text)
        else:
          c_num = 0

      # print(title.text)
      tz = datetime.timezone(datetime.timedelta(hours=9))
      a = datetime.datetime.now(tz)
      t = a.strftime('%Y%m%d%H%M%S')
      # print("{0} title:{1}\nmedia:{2} comment number:{3}, post time:{4}, scrape_time:{5} url:{6}".format(num, title_name, media_name, c_num, release_time, t, url))
      df_add = pd.DataFrame(data = np.array([[title_name, media_name, c_num, release_time, t,  url]]), index=[0], columns=['text', 'media', 'cmt', 'p_time', 's_time', 'link'])
      df = pd.concat([df, df_add])

    # tz = datetime.timezone(datetime.timedelta(hours=9))
    # a = datetime.datetime.now(tz)
    # b = str(a.date())[5:] + "," + str(a.time())[:5]
    # df.to_csv('/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/csv 主要トピック/主要{}.csv'.format(b), index = False)
    with open('/Users/yoshiharatatsuhito/Desktop/T.Yoshihara/計算社会科学/Python_code/yahoo_analysis/csv 主要トピック/主要.csv', 'a') as f:
        writer = csv.writer(f, lineterminator='\n')
        for ary in df.values:
            writer.writerow(ary)
