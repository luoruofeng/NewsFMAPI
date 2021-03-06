# coding=utf-8
import sys
import json
import os

import time
import errno
import logging
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
import json
from aip import AipSpeech
import subprocess
import threading

#项目的根目录 /voice
BASE_PATH=os.path.dirname(os.path.abspath(__file__))
#将根目录添加到sys.path 系统便可以查找到该项目下的模块
sys.path.append(BASE_PATH)

import mongo_opt

"""
这个程序（进程）将一直去读取pipe（有名管道）
将管道中的json转成dict，并将文章内容转化为音频
将过长的文章转化为多个音频后，进行合并（ffmpeg）

百度api语言在线合成的QPS是10个（企业认证），也就是可以启动10根线程同时转化音频
"""

""" 你的 APPID AK SK """
APP_ID = '18537748'
API_KEY = 'mrgLHsuD2jUVSRNdD7LE9P44'
SECRET_KEY = 'wbxfMAdQRD6YnnMFNldGWSOvjGVl9w4i'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

MAX_FONT = 2048

# 发音人选择, 基础音库：0为度小美，1为度小宇，3为度逍遥，4为度丫丫，
PER = 0
# 语速，取值0-15，默认为5中语速
SPD = 6
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

#pipe路径
FIFO = "/article_pipe"
#音频保存路径
VOICE_DIR = "/voice/"
#音频格式
FORMAT = ".mp3"

class DemoError(Exception):
    pass


TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'
SCOPE = 'audio_tts_post'  # 有此scope表示有tts能力，没有请在网页里勾选

def fetch_token():
    # print("fetch token begin")
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
        # print('token http response http code : ' + str(err.code))
        result_str = err.read()
    if (IS_PY3):
        result_str = result_str.decode()

    result = json.loads(result_str)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not SCOPE in result['scope'].split(' '):
            raise DemoError('scope is not correct')
        return result['access_token']
    else:
        pass


"""  TOKEN end """

def baidu_voice(params):
    data = urlencode(params)
    # print('test on Web Browser' + TTS_URL + '?' + data)

    req = Request(TTS_URL, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()

        headers = dict((name.lower(), value) for name, value in f.headers.items())

        has_error = ('content-type' not in headers.keys() or headers['content-type'].find('audio/') < 0)
    except  URLError as err:
        # print('asr http response http code : ' + str(err.code))
        result_str = err.read()
        has_error = True

    return result_str,has_error


#保存对象为音频
def opt(obj):
    # json字符串 转 dict
    print(obj)
    obj_dict = json.loads(obj, encoding="UTF-8")
    tex = obj_dict["content"]
    title = obj_dict["title"]

    # 分割文字  百度能接受的最大长度是2048
    counter = 1
    current_index = 0

    need_merge_dict = {title+FORMAT:[]}
    while True:
        part_text = tex[current_index:current_index + MAX_FONT]
        current_index += MAX_FONT
        if (part_text == ""):
            break

        if (len(tex) <= MAX_FONT):
            subtitle = title
        else:
            subtitle = title + str(counter)
            need_merge_dict[title+FORMAT].append(subtitle+FORMAT)

        counter += 1

        params = {'tok': token, 'tex': part_text, 'per': PER, 'spd': SPD, 'pit': PIT, 'vol': VOL, 'aue': AUE,
                  'cuid': CUID, 'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数

        result_str, has_error = baidu_voice(params)

        # 音频文件 保存
        save_file = "error.txt" if has_error else VOICE_DIR + subtitle + FORMAT
        with open(save_file, 'wb') as of:
            of.write(result_str)

        if has_error:
            result_str = str(result_str, 'utf-8')
            # print("tts api  error:" + result_str)

        print("result saved as :" + subtitle)
        logging.info("result saved as :" + subtitle)

    #合并较长音频
    if (len(need_merge_dict[title+FORMAT]) > 0):
        merge_voice(need_merge_dict,title+FORMAT)
        delete_sub_voice(need_merge_dict[title+FORMAT])

def loopPipe():
    # 循环读取pipe管道中的json
    while True:
        logging.info("waiting for new data be sent to pipe")
        #如果没有写管道打开，将会阻塞在这里。
        # 如果有写管道打开：则开始是读取.
        # 如果写管道关闭：则会读取到空
        # continue结束本次循环，再次阻塞在这里。
        #写管道的 最多一个进程 因为如果写管道有多个进程并且速度比读管道的频率要高，在读管道打开瞬间，所有进程上的写管道都将内容写入同一个文件，读取后，将分不清写入的个数。
        #如果写管道在一个进程上，而读管道可以在多个进程上，因为写管道打开的时候只会有其中一个进程上的读管道与之对应。
        # 就算写管道的打开频率比读管道高，也不会有问题，因为读管道里，有判断len(data)。如果为空，表示写管道已经关闭，一次写入完成，写管道再次阻塞，等到读管道再次运行到这里，写管道才能再次写入。
        with open(FIFO, 'r') as rf:
            obj = rf.read()
            logging.info("read pipe... font size:"+str(len(obj)))
            if(len(obj) == 0):
                continue
        #对读取到的字符串对象进行操作
        try:
            opt(obj)
        except Exception as e:
            print("对读取到的字符串对象进行操作错误!")
            print(e)
            mongo_opt.setUnavailable(obj["url"])

def init_log():
    # 创建一个logging对象
    logger = logging.getLogger()
    # 创建一个文件对象  创建一个文件对象,以UTF-8 的形式写入 baidu_log.log 文件中
    fh = logging.FileHandler('baidu_log.log', encoding='utf-8')
    # 创建一个屏幕对象
    sh = logging.StreamHandler()
    # 配置显示格式  可以设置两个配置格式  分别绑定到文件和屏幕上
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
    fh.setFormatter(formatter)  # 将格式绑定到两个对象上
    sh.setFormatter(formatter)

    logger.addHandler(fh)  # 将两个句柄绑定到logger
    logger.addHandler(sh)

    logger.setLevel(10)  # 总开关
    fh.setLevel(10)  # 写入文件的从10开始
    sh.setLevel(30)  # 在屏幕显示的从30开始


    # ffmpeg不支持MP3
    # 所以安装ffmpeg时候需要先安装lame
    #
    # 合并命令：
    # ffmpeg -i 马斯克：下一步我干啥，你猜1.mp3 -i 马斯克：下一步我干啥，你猜2.mp3 -i 马斯克：下一步我干啥，你猜3.mp3 -i 马斯克：下一步我干啥，你猜4.mp3 -filter_complex '[0:0] [1:0] concat=n=4:v=0:a=1 [a]' -map [a] new4.mp3
    # n=4代表视频个数

#need_merge_dict 是dict  key是标题 value是subtitle列表
#如{"马斯克：下一步我干啥，你猜.mp3":
# ["马斯克：下一步我干啥，你猜1.mp3",
# "马斯克：下一步我干啥，你猜2.mp3",
# "马斯克：下一步我干啥，你猜3.mp3",
# "马斯克：下一步我干啥，你猜4.mp3",]}
def merge_voice(need_merge_dict,title):
    exec_str = "ffmpeg"

    for input_voice in need_merge_dict[title]:
        exec_str+=" -i"
        input_voice = input_voice.replace(' ','\\ ')
        exec_str+=(" "+VOICE_DIR+input_voice)

    exec_str+=" -filter_complex '[0:0] [1:0] concat=n="+str(len(need_merge_dict[title]))+":v=0:a=1 [a]' -map [a]"
    exec_str+=(" "+VOICE_DIR+title.replace(' ','\\ '))
    p = subprocess.Popen(exec_str,shell=True)
    #communicate或wait方法可以等待合并完成后继续执行，不然Popen是个非阻塞的方法,如果不用Popen，也用阻塞式的方法call。
    out, err = p.communicate()


def delete_sub_voice(voices):
    for voice in voices:
        try:
            os.remove(VOICE_DIR+voice)
        except Exception as e:
            print("delete failed!!")
            print(e)

if __name__ == '__main__':
    init_log()

    #创建文件夹存放音频文件
    if(os.path.exists(VOICE_DIR) == False):
        os.mkdir(VOICE_DIR)

    try:
        os.mkfifo(FIFO)
    except OSError as e:
        if (e.errno != errno.EEXIST):
            raise

    #baidu voice
    token = fetch_token()
    has_error = None

    loopPipe()
    #可以使用10个线程进行转化
    # for i in range(10):
    #     t = threading.Thread(target=loopPipe,args=())
    #     #非守护线程
    #     t.setDaemon(False)
    #     t.start()
