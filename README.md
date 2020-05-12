# piapro_tool
解析piapro.jp的音频链接，或者下载图片。<br>
# Version
Python3
# Use
```sh
pip install requests
pip install win32-setctime
python piapro.py login username password #Do login and save cookies
python piapro.py https://piapro.jp/t/d8wT # 音乐
python piapro.py auth shinra_logic #Download whole library of the author shinra_logic
```
# Output
```sh
[歌名] [P主] [音频地址]
['ある計画は今も密かに'] ['森羅さん'] ['https://cdn.piapro.jp/mp3_a/p4/p4kt7qabi367tjst_20190312003936_audition.mp3']
```
# notice
链接如果是图片，会直接下载。<br>
**下载图片必须要登录，请在piapro.py里填好帐号密码！**
