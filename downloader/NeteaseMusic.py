from util.Request import Request
from util.AES import AESCipher
import json
import time

class NeteaseMusic(object):

    def __init__(self):
        self.config = {
            'nonce': '0CoJUm6Qyw8W8jud',
            'secretKey': 'TA3YiYCfY2dDJQgg',
            'encSecKey': '84ca47bca10bad09a6b04c5c927ef077d9b9f1e37098aa3eac6ea70eb59df0aa28b691b7e75e4f1f9831754919ea784c8f74fbfadf2898b0be17849fd656060162857830e241aba44991601f137624094c114ea8d17bce815b0cd4e5b8e2fbaba978c6d1d14dc3d1faf852bdd28818031ccdaaa13a6018e1024e2aae98844210',
            'IV': '0102030405060708'
        }

    # aes-128-cbc
    def aesEncode(self, data, key):
        return AESCipher(key=key).encrypt(data, self.config['IV'])

    def prepare(self, data):
        result = { 'params': self.aesEncode(json.dumps(data), self.config['nonce']) }
        result['params'] = self.aesEncode(result['params'], self.config['secretKey'])
        result['encSecKey'] = self.config['encSecKey']
        return result

    # 搜索歌曲
    def search(self, keyword):
        response = Request.jsonGet(url='http://s.music.163.com/search/get/', params={
            'type': 1,
            's': keyword
        })
        if 'code' in response and response['code'] == 200:
            return response['result']['songs']
        else:
            return []
    pass

    # 批量获取歌曲链接
    def getUrl(self, songIds):
        response = Request.jsonPost(url='http://music.163.com/weapi/song/enhance/player/url?csrf_token=', params=self.prepare({
            'ids': songIds,
            'br': 999000,
            'csrf_token': ''
        }))

        # 解析response
        if 'code' in response and response['code'] == 200:
            if 'data' in response:
                return response['data']
            else:
                return []
        else:
            return None
    
    # 获取单一歌曲链接
    def getSingleUrl(self, songId):
        result = self.getUrl([songId])
        if result == None:
            return result
        elif len(result) == 0:
            return {}
        else:
            return result[0]

    def download(self, songId, filename=None, callback=None):
        # 名称处理
        if not filename:
            filename = str(int(time.time()))

        # 获取歌曲并下载
        musicResult = self.getSingleUrl(songId)
        if musicResult and 'url' in musicResult:
            musicUrl = musicResult['url']
            Request.download(musicUrl, './downloader/download/%s.mp3' % filename, callback)
        else:
            return False