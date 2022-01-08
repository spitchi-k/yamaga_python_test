import requests
from bs4 import BeautifulSoup
import lxml.html
import time

page_url_origin = "hogehoge"  # 画像サイトのURLを指定

for i in range(0,2):
  images = []
  page_url = page_url_origin + "&page=" + str(i+1)
  soup = BeautifulSoup(requests.get(page_url).content, 'lxml')

  #画像URLの取得
  for link in soup.find_all("img"):
    if link.get("src").startswith("https"):
      if link.get("src").endswith(".png"):
        images.append(link.get("src"))

  #画像の保存
  for target in images: 

    img_name = target[45:55] + ".png"
    if img_name.startswith("2020"):
      print("out_image")
      continue
    print(img_name)
    re = requests.get(target)
    with open('img/' + img_name, 'wb') as f:
      f.write(re.content)
    time.sleep(1)