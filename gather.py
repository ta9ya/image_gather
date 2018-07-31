from urllib.request import urlopen, Request
from urllib.parse import quote
from mimetypes import guess_extension
import os
import sys
import numpy as np
from bs4 import BeautifulSoup
from time import time, sleep
from facer import Facer

MY_UA = ''


class Fetcher:
	'''
	受け取ったurlを指定されたuaでリクエストし、html、MIMEタイプとエンコード（Content-Type）を貰う
	'''
	def __init__(self, ua=''):
		self.ua = ua

	def fetch(self, url):
		req = Request(url, headers={'User-Agent': self.ua})
		try:
			with urlopen(req, timeout=3) as p:
				content = p.read()
				mime = p.getheader('Content-Type')
		except:
			sys.stderr.write('Error in fetching :'+ format(url) + "\n")

			return None, None

		return content, mime


def html_scraping(url):
	img_link_elem = []
	byte_content, mime = fetcher.fetch(url)

	# html analyze by bs4
	soup = BeautifulSoup(byte_content.decode('UTF-8'), 'html.parser')
	elem = soup.find_all('img')
	img_link_elem.extend(elem)
	img_urls = [e.get('src') for e in img_link_elem]

	return img_urls


def url_search(word, n):
	'''
	ヤフーの画像検索を使って画像収集
	:param word: 検索キーワード
	:param n: 枚数
	:return: 画像のURL群　これをpcのフォルダにDLして終わり
	'''
	code = '&ei=UTF-8'
	img_urls = []

	if 60 < n:
		iter_num = int(n / 60)
		rem = n % 60
		print(iter_num)
		for i in range(2, iter_num+2):
			url = ('https://search.yahoo.co.jp/image/search?n=60&p={}{}' + code).format(quote(word), i)
			img_urls += html_scraping(url)
		if rem != 0:
			url = ('https://search.yahoo.co.jp/image/search?n={}&p={}').format(rem, quote(word))
			img_urls += html_scraping(url)
	elif 0 < n < 60:
		url = ('https://search.yahoo.co.jp/image/search?n={}&p={}'+code).format(n, quote(word))
		img_urls += html_scraping(url)
	else:
		raise ValueError('Enter a number larger than 1.')

	#重複を取り除くテク
	img_urls = list(set(img_urls))
	return img_urls


def image_collector_in_url(urls, fname, command):
	'''
	取得したURL群をfetchし画像ダウンロード
	:param urls:  画像の存在するURL
	:param fname: 作成されるフォルダの名前
	:param command: 顔の編集モード指定番号
	:return: ダウンロードに成功した数
	'''

	dir = 'img/'+str(fname)
	scount = 0

	# create new directory
	if not os.path.exists(dir):
		os.makedirs(dir)

	for i, url in enumerate(urls):
		sleep(0.1)
		img, mime = fetcher.fetch(url)
		if not mime or not img:
			continue
		try:
			ext = guess_extension(mime.split(';')[0])
			if ext in ('.jpeg', '.jpg', '.png', '.jpe'):
				ext = '.png'
			elif not ext:
				continue
		except:
			print('Error in converting extension')
			continue

		if ext in ('.jpeg', '.jpg', '.png', '.jpe'):
			file = os.path.join(dir, str(i) + ext)
			command_dict = {
				0: (lambda encode: facer.draw_rect(encode)),
				1: (lambda encode: facer.cut_face(encode))
			}
			print('file:' + file)
			# print(img)

			#顔編集実行
			if command in command_dict.keys():
				encode = np.asarray(bytearray(img), dtype=np.uint8)
				img = command_dict[command](encode)
				facer.save_img(img, file)
				print('ダウンロード成功 URL:'+str(url))
				scount += 1
			else:
				with open(file, mode='wb') as f:
					f.write(img)
				print('ダウンロード成功 URL:'+str(url))
				scount += 1
		else:
			print('(Image file that is not saved.)')

	return scount


def enter_number():
	get_num = input('>> ')
	while not get_num.isnumeric():
		print('enter by number')
		get_num = input('>> ')
	return int(get_num)


def enter_command():
	command = input('>> ')
	while True:
		if command in ['0', '1', '2']:
			return int(command)
		else:
			print('輪郭描画:0　顔のみ切り出し:1　編集なし:2')
			command = input('>> ')


if __name__ == '__main__':

	fetcher = Fetcher(MY_UA)
	facer = Facer()

	print('欲しい画像のキーワードを入力してください')
	keyword = input('>> ')
	print('枚数を入力してください')
	get_num = enter_number()
	# get_num = int(input('>> '))
	print('顔の編集モードを指定してください　輪郭描画:0　顔のみ切り出し:1　編集なし:2')
	command = enter_command()
	image_urls = url_search(keyword, get_num)
	print(str(len(image_urls))+'枚の画像URLの取得に成功しました')
	download_count = image_collector_in_url(image_urls, keyword, command)
	print(str(download_count)+'件の画像の収集に成功しました')