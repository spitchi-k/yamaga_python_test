import pyocr
from PIL import Image, ImageEnhance
import os
import pathlib
import re
import cv2

###################################
# 設定値
###################################
TESSERACT_PATH  = '/usr/local/Cellar/tesseract/5.0.0'
TESSDATA_PATH   = '/usr/local/Cellar/tesseract/5.0.0/share/tessdata'
os.environ["PATH"] += os.pathsep + TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH

#name = "2021_arai"
#name = "2021_asada"
#name = "2021_baisu"
#name = "2021_hashi"
#name = "2021_ohi"
#name = "2021_ohno"
#name = "2021_urakami"
name = "2021_yamamoto"


###################################
# メソッド
###################################

#スタッツの画像データから数値を抽出する
def get_stats_data(img_path, trimming_pattern):

  #OCRエンジン取得
  tools = pyocr.get_available_tools()
  tool = tools[0]

  #OCRの設定
  builder = pyocr.builders.TextBuilder(tesseract_layout=6)

  #解析画像読み込み
  img_origin = cv2.imread(img_path)

  #OCR前の画像処理
  #1.トリミング
  if trimming_pattern == "2021_attack":
    img = img_origin[80 : 460 , 632 : 673]
  elif trimming_pattern == "2021_defense":
    img = img_origin[80 : 416 , 300 : 340]
  else:
    img = img

  #2.グレースケール
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  #3.2値化
  threshold = 100
  ret, img = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)

  #画像からOCRで日本語を読んで、文字列として取り出す
  pil_img = Image.fromarray(img)
  txt_pyocr = tool.image_to_string(pil_img, lang='jpn', builder=builder)

  #半角スペースの削除
  txt_pyocr = txt_pyocr.replace(' ', '')

  #数値の抽出
  stats = re.findall(r"\d+", txt_pyocr)
  #print(stats)

  #forデバッグ:画像の表示
  #cv2.imshow('after', img)
  #cv2.waitKey(0)
  #cv2.destroyAllWindows()

  return stats


###################################
# main 
###################################

atk_stats_list = []
dfs_stats_list = []

print(">>> target = " + name)

#画像ファイルからstatsを取得しlist化
#1.攻撃スタッツ
game_num = 0
img_root_path = "./img/" + name + "/atk/" 
img_names = list(pathlib.Path(img_root_path).glob('*.png'))
for img_path in img_names:
  game_num += 1
  img_path = img_root_path + img_path.name
  #print(img_path)
  stats = get_stats_data(img_path, "2021_attack")
  atk_stats_list.append(stats)

#2.守備スタッツ
img_root_path = "./img/" + name + "/dfs/" 
img_names = list(pathlib.Path(img_root_path).glob('*.png'))
for img_path in img_names:
  img_path = img_root_path + img_path.name
  #print(img_path)
  stats = get_stats_data(img_path, "2021_defense")
  dfs_stats_list.append(stats)

#Statsの計算(合計値の算出)
atk_stats_sum = [0] * 8
dfs_stats_sum = [0] * 7
offset = 1   #出場時間が90分未満の場合, 補正する
#1.攻撃スタッツ
for stats in atk_stats_list:
  #print(stats)
  if int(stats[0]) < 15:  #出場時間が15分未満の場合は除外する
    game_num -= 1
    continue 
  if int(stats[0]) < 90:
    offset = 90 / int(stats[0])
  else:
    offset = 1
  #print("offset = %s" % offset)
  for i in range(0,8):
    atk_stats_sum[i] += int(stats[i+1]) * offset
#2.攻撃スタッツ
for stats in dfs_stats_list:
  #print(stats)
  if int(stats[0]) < 15:  #出場時間が15分未満の場合は除外する
    #game_num -= 1
    continue 
  if int(stats[0]) < 90:
    offset = 90 / int(stats[0])
  else:
    offset = 1
  #print("offset = %s" % offset)
  for i in range(0,7):
    dfs_stats_sum[i] += int(stats[i+1]) * offset

#Statsの計算(平均値の算出)
atk_stats_ave = [0] * 8
dfs_stats_ave = [0] * 7
#1.攻撃スタッツ
for i in range(0,8):
  atk_stats_ave[i] = round((atk_stats_sum[i]/game_num),2)
#2.守備スタッツ
for i in range(0,7):
  dfs_stats_ave[i] = round((dfs_stats_sum[i]/game_num),2)

print("*** 1試合(90分)あたりの平均値 ***")
print("<< 攻撃スタッツ >>")
print("ゴール       : %s" % atk_stats_ave[0])
print("シュート     : %s" % atk_stats_ave[1])
print("枠内シュート : %s" % atk_stats_ave[2])
print("アシスト     : %s" % atk_stats_ave[3])
print("パス         : %s" % atk_stats_ave[4])
print("パス成功     : %s (%s)" % (atk_stats_ave[5], round((atk_stats_ave[5]/atk_stats_ave[4]*100),1)))
print("ラストパス   : %s" % atk_stats_ave[6])
print("クロス       : %s" % atk_stats_ave[7])

print("")

print("<< 守備スタッツ >>")
print("タックル       : %s" % dfs_stats_ave[0])
print("タックル成功   : %s (%s)" % (dfs_stats_ave[1], round((dfs_stats_ave[1]/dfs_stats_ave[0]*100),1)))
print("クリア         : %s" % dfs_stats_ave[2])
print("ブロック       : %s" % dfs_stats_ave[3])
print("こぼれ球奪取   : %s" % dfs_stats_ave[4])
print("ファウル       : %s" % dfs_stats_ave[5])
print("警告           : %s" % dfs_stats_ave[6])
