import requests
import re
import sys
import time
import http.cookiejar
import os.path
from win32_setctime import setmtime
from html import unescape
import time, datetime
import glob
import urllib.parse

def sanitize_filename(filename):
	return filename.replace("/", "／")\
				   .replace(":", "։")\
				   .replace("*", "＊")\
				   .replace("?", "？")\
				   .replace("<", "ᐸ")\
				   .replace(">", "ᐳ")\
				   .replace("|", "⎸")\
				   .replace("\"", "“")

def login():

	data = {
		'_username': username,
		'_password': password,
		'_remember_me': 'on',
		'login': 'ログイン'
	}
	
	r1 = s.get('https://piapro.jp/')
	r = s.post('https://piapro.jp/login/exe', data = data, allow_redirects=False)
	
	s.cookies.save()
	
	return s.cookies

def get_info(url):

	r = requests.get(url)

	contentId = re.findall('contentId:\'(.+?)\',', r.text)[0]
	createDate = re.findall('createDate:\'(.+?)\',', r.text)[0]

	return contentId, createDate

def get_mp3(url, contentAuth = None):
	id = url[-4:]
	
	contentId, createDate = get_info(url)
	htmlURL = f'https://piapro.jp/html5_player_popup/?id={contentId}&cdate={createDate}&p=0'
	
	r = requests.get(htmlURL)

	title = re.findall("title: '(.+?)'", r.text)[0]
	artist = re.findall("artist: '(.+?)'", r.text)[0]
	mp3 = re.findall("mp3: '(.+?)'", r.text)[0]
	#date = re.findall("\<p class\=\"date\"\>投稿日時\：\<span\>(.+?)\<\/span\>\<\/p\>", r.text)[0]
	
	r2 = requests.get(mp3)
	title = unescape(title)
	artist = unescape(artist)
	
	if contentAuth is not  None:
		filename = f"{contentAuth}\{id} - {title} - {artist}.mp3"
	else:
		filename = f"{id} - {title} - {artist}.mp3"
	
	filename = sanitize_filename(filename)
	
	with open(filename, 'wb') as f2:
		f2.write(r2.content)
		f2.close()
	
	setmtime(filename, time.mktime(datetime.datetime.strptime(createDate, "%Y%m%d%H%M%S").timetuple()))

def get_img(url):
	
	id = url[-4:]
	
	cookies = s.cookies

	r = s.get(url, cookies = cookies)
	
	html = r.text
	downAllowed = True
	try:
		contentId = re.findall('contentId: \'(.+?)\'', html)[0]
		contentName = re.findall('\<h1 class\=\"cd_works-title\"\>(.+?)\<\/h1\>', html)[0]
		contentAuth = re.findall('cd_user-name\" href\=\"\/(.+?)\"\>', html)[0]
		createDate = re.findall('createDate]" required="required" value="(.+?)"', html)
		if len(createDate) == 0:
			downAllowed = False
			thumbUrl = re.findall("\<meta name\=\"twitter\:image\" content\=\"(.+?)\"\>", html)[0]
			createDate = re.findall('\<span\>投稿日\：\<\/span\>(.+?)\s+\|', html)[0]
			createDate = createDate[0:4] + createDate[5:7] + createDate[8:10] + createDate[11:13] + createDate[14:16] + createDate[17:19]
		else:
			createDate = createDate[0]
			license = re.findall('license]" required="required" value="(.+?)"', html)[0]
			
		folderId = re.findall('defaultFolderId:(.+?),', html)[0]
		token = re.findall('_token]" value="(.+?)"', html)[0]
	except Exception as e:
		exp = str(e)
		print(exp)
		
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		print(exc_type, fname, exc_tb.tb_lineno)
		
		return False
	
	if downAllowed:
		data = {
		'DownloadWithBookmark[contentId]': contentId,
		'DownloadWithBookmark[createDate]': createDate,
		'DownloadWithBookmark[license]': license,
		'DownloadWithBookmark[folderId]': folderId,
		'DownloadWithBookmark[_token]': token,
		}

		r1 = s.post('https://piapro.jp/download/content_with_bookmark/', data, stream=True)
		Type = r1.headers['Content-Type']
		file_size = r1.headers['Content-Length']

		if Type == 'image/jpeg':
			suffix = '.jpg'
		elif Type == 'image/png':
			suffix = '.png'
		elif Type == 'image/gif':
			suffix = '.gif'
		else:
			suffix = ''
	else:
		suffix = ".thumb." + thumbUrl.split(".")[-1]
		r1 = s.get(thumbUrl)
	
	contentName = unescape(contentName)
	
	filename = f"{contentAuth}\{id} - {contentName}{suffix}"
	filename = sanitize_filename(filename)
	
	with open(filename, 'wb') as f2:
		f2.write(r1.content)
		f2.close()
	
	setmtime(filename, time.mktime(datetime.datetime.strptime(createDate, "%Y%m%d%H%M%S").timetuple()))
	
	return True

def main(url, auth = None):

	r = requests.get(url)

	category = re.findall('view:\'(.+?)\'', r.text)[0]

	if category == 'audio':
		return get_mp3(url, auth)
	elif category == 'image':
		return get_img(url)
	elif category == 'text':
		return True
	else:
		return False
		
def down_auth(auth, last):
	start = 0
	found = 35
	
	authFolder = auth + "\\"
	
	if not os.path.exists(os.path.dirname(authFolder)):
		os.makedirs(os.path.dirname(authFolder))
	
	if last is None:
		list_of_files = glob.glob(os.path.abspath(authFolder + "*"))
		if len(list_of_files) != 0:
			latest_file = max(list_of_files, key=os.path.getmtime)
			last = os.path.basename(latest_file)[0:4]
		
	cookies = s.cookies
	
	while found >= 35:
		url = f"https://piapro.jp/my_page/?pid={auth}&view=content&start_rec={start}&order=sd"
		
		r = s.get(url, cookies = cookies)
		html = r.text
		
		ids = re.findall("href=\"\/t\/(.+?)\"", html)
		ids = [elem for i, elem in enumerate(ids) if i == 0 or ids[i-1] != elem]
		
		found = len(ids)
		
		for id in ids:
			if last is not None and id == last:
				return
			
			itemURL = f"https://piapro.jp/t/{id}"
			
			result = main(itemURL, auth)
			if not result:
				print(id)
		
		start = start + found
	
if __name__ == '__main__':
	username = ''
	password = ''
	
	s = requests.session()
	s.cookies = http.cookiejar.LWPCookieJar(filename="cookies.txt")
	
	url = sys.argv[1]
	
	
	if url == "login":
		username = sys.argv[2]
		password = sys.argv[3]
		
		login()
	else:
		s.cookies.load()
		
		if url == "auth":			
			auth = sys.argv[2]
			last = None
			
			if len(sys.argv) > 3:
				last = sys.argv[3]
			
			down_auth(auth, last)
		else:
			main(url)
