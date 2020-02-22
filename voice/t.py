# coding=utf-8
import sys
import json
import os
import time
import errno
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus

from aip import AipSpeech

""" 你的 APPID AK SK """
APP_ID = '18537748'
API_KEY = 'mrgLHsuD2jUVSRNdD7LE9P44'
SECRET_KEY = 'wbxfMAdQRD6YnnMFNldGWSOvjGVl9w4i'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

MAX_FONT = 2048

# 发音人选择, 基础音库：0为度小美，1为度小宇，3为度逍遥，4为度丫丫，
PER = 0
# 语速，取值0-15，默认为5中语速
SPD = 5
# 音调，取值0-15，默认为5中语调
PIT = 5
# 音量，取值0-9，默认为5中音量
VOL = 5
# 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
AUE = 3

FORMATS = {3: "mp3", 4: "pcm", 5: "pcm", 6: "wav"}
FORMAT = FORMATS[AUE]

CUID = "123456PYTHON"

TTS_URL = 'http://tsn.baidu.com/text2audio'


class DemoError(Exception):
    pass


TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'
SCOPE = 'audio_tts_post'  # 有此scope表示有tts能力，没有请在网页里勾选

def fetch_token():
    print("fetch token begin")
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()
    if (IS_PY3):
        result_str = result_str.decode()

    print(result_str)
    result = json.loads(result_str)
    print(result)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not SCOPE in result['scope'].split(' '):
            raise DemoError('scope is not correct')
        return result['access_token']
    else:
        pass


"""  TOKEN end """

if __name__ == '__main__':
    FIFO = "mypipe2"
    VOICE_DIR = "/voice/"

    if(os.path.exists(VOICE_DIR) == False):
        os.mkdir(VOICE_DIR)

    try:
        os.mkfifo(FIFO)
    except OSError as e:
        if (e.errno != errno.EEXIST):
            raise

    token = fetch_token()
    has_error = None
    FORMAT = ".mp3"
    save_file = "error.txt" if has_error else 'result' + FORMAT

    with open(FIFO, 'r') as rf:
        tex = rf.read()
        tex = quote_plus(tex)

    title = "我是标题"
    counter = 0
    current_index = 0
    while True:
        if(counter == 0):
            subtitle = title
        else:
            subtitle = title + str(counter)
        counter += 1

        part_text = tex[current_index:current_index+MAX_FONT]
        current_index += MAX_FONT
        if(part_text == ""):
            break
        current_index+=MAX_FONT

        params = {'tok': token, 'tex': part_text, 'per': PER, 'spd': SPD, 'pit': PIT, 'vol': VOL, 'aue': AUE, 'cuid': CUID, 'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数

        data = urlencode(params)
        print('test on Web Browser' + TTS_URL + '?' + data)

        req = Request(TTS_URL, data.encode('utf-8'))
        has_error = False
        try:
            f = urlopen(req)
            result_str = f.read()

            headers = dict((name.lower(), value) for name, value in f.headers.items())

            has_error = ('content-type' not in headers.keys() or headers['content-type'].find('audio/') < 0)
        except  URLError as err:
            print('asr http response http code : ' + str(err.code))
            result_str = err.read()
            has_error = True

        save_file = "error.txt" if has_error else VOICE_DIR + subtitle + FORMAT
        with open(save_file, 'wb') as of:
            of.write(result_str)

        if has_error:
            if (IS_PY3):
                result_str = str(result_str, 'utf-8')
            print("tts api  error:" + result_str)

        print("result saved as :" + subtitle)
