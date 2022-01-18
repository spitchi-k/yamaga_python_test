# 参考
# select()の使い方：https://gammasoft.jp/blog/difference-find-and-select-in-beautiful-soup-of-python/#all-5

"""
<<仕様書>> 
[本コードの目的]
"Football LAB"ページにて、全チーム/全選手のPlayingStayleを取得し、表にまとめる

[設計]
・WEBスクレイピング
・Step1. 各チームのURLを取得する
    ルール > https://www.football-lab.jp/ + XXX
    XXX → TOPページにて取得可能。
    https://www.football-lab.jp/
    → 例) <a href="/sapp/">
・Step2. 各選手のURLを取得する：
    ルール > https://www.football-lab.jp/ + YYY
    YYY → 所属チームのWEBページにて取得可能
    → 例) <a href="/player/700774/">土井　康平</a>
・Step3. PlayingStayleを取得する：
    選手のWEBページにて取得可能
    → 例) <a href="/summary/player_parameter/j3/?data=1&amp;year=2021">決定力</a>
            <span class="numL">11</span> 
"""

import requests
from bs4 import BeautifulSoup
import openpyxl as excel
import time

######################################
# 設定値
######################################
MAIN_PAGE_URL = "https://www.football-lab.jp"  #FootballLAB_Topページ 
BOOK_NAME     = "PlayingStyle_2021_AllTeam.xlsx"


######################################
# method
######################################

# 対象Playerの"PlayingStayle"を取得する
def get_playing_stayle(player_url):

  style_data = []
  soup = BeautifulSoup(requests.get(player_url).content, 'lxml')

  name = "xxx"
  for link in soup.select("span.jpn"):
    name = link.getText()
    style_data.append(name)
    break
  print("[DEBUG] Player Name : %s" % name)  #1選手として, 見やすく出力する

  for link in soup.select("span.numL"):
    if 1 <= len(link.getText()) and len(link.getText()) <= 2:
      if link.getText() == '-':
        style_data.append(link.getText())
      else:
        style_data.append(int(link.getText()))

  return style_data


######################################
# main
######################################

#新規ブックを作成
book = excel.Workbook()

#全てのチームのURLを取得する
team_urls = []
team_names = []
soup = BeautifulSoup(requests.get(MAIN_PAGE_URL).content, 'lxml')
for link in soup.select('a'):
  if link.get("title"):               #条件 > タグ:'a' && "title"属性を持つ
    team_url = MAIN_PAGE_URL + link.get("href")
    team_name = link.get("title")
    #print("[DEBUG] team_url = %s,   team_name = %s" % (team_url, team_name) )
    team_urls.append(team_url)
    team_names.append(team_name)

#全チームの各選手のplayingStyleの取得
player_urls = []
j = 0
for team_url in team_urls:
  print(">>> Team名 : %s" % team_names[j])

  #対象チーム用のsheetを作成する
  sheet = book.create_sheet(title = team_names[j])
  #sheet.append(["選手名", "FinshiSkill", "O-Shoot", "H-Shoot", "L-Shoot", "SP-Shoot", "PassResponse", "AerialDuel(enemy)", "DribbleCH", "CrossCH", "PassCH", "BuildUp", "AerialDuel(own)", "Defense", "BallRecovery", "CoverErea"])
  sheet.append(["選手名","決定力","OTシュート","Hシュート","Lシュート","SPシュート","パスRP","敵陣空中戦","ドリブルCH","クロスCH","パスCH","ビルドアップ","自陣空中戦","守備","ボール奪取","カバーエリア"])

  j += 1
  soup = BeautifulSoup(requests.get(team_url).content, 'lxml')
  #対象チームの"2021シーズンに出場機会のあった"全選手のURLを取得する
  i = 0
  player_urls.clear()
  for link in soup.select('a'):
    if link.get("href"):
      if link.get("href").startswith("/player"):    #条件 > タグ:'a' && 'href'属性を持つ && 'href'の属性値の先頭文字が "/player"      
        i += 1
        if i > 15:  #上記抽出方法だと"ゴールランキング"からも情報が取れてしまうので、暫定対策
          player_url = MAIN_PAGE_URL + link.get("href")
          player_urls.append(player_url)
          #print("[DEBUG] player_url = %s" % player_url )
  
  #各選手のPlayingStyleを出力する
  for player_url in player_urls:
    time.sleep(0.1)
    style_data = get_playing_stayle(player_url)
    #print(style_data)
    sheet.append(style_data)
  
#ファイルに保存
book.save(BOOK_NAME)
print('make file ... OK >> %s' % BOOK_NAME)
