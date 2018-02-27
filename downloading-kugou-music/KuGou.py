# -*- coding: utf-8 -*-
import requests
import json


class KuGou(object):
    def __init__(self, search_music):
        self.search_song = "http://songsearch.kugou.com/song_search_v2?"
        self.search_music = search_music
        self.music_url = "http://www.kugou.com/yy/index.php?r=play/getdata&"
        self.headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)"
        }

    def send_request(self, url, params=None):
        response = requests.get(url, params=params, headers=self.headers)
        data = response.content
        # print(response.url)
        return data

    def download_music(self, music, music_name):
        path = "./music/"
        music_name += ".mp3"
        with open(path + music_name, "wb") as f:
            f.write(music)
            print("%s下载成功" % music_name)

    def handle_json_data(self, json_data, flag):
        json_to_dict = json.loads(json_data)
        musics_info = json_to_dict['data']

        if flag == 1:
            # 获取歌曲的详细信息
            musics_info = musics_info['lists']
            musics_list = list()
            for music_info in musics_info:
                music_info_dict = dict()
                music_info_dict['music_name'] = music_info['FileName']
                music_info_dict['FileHash'] = music_info['FileHash']
                music_info_dict['HQFileHash'] = music_info['HQFileHash']
                music_info_dict['AlbumID'] = music_info['AlbumID']
                musics_list.append(music_info_dict)
            return musics_list
        elif flag == 2:
            # 获取歌曲的下载链接
            download_url_list = list()
            download_url_list.append(musics_info['play_url'])
            return download_url_list

    def download_mange(self, musics_lists):
        """下载管理"""
        download_list = list()
        for index, music in enumerate(musics_lists):
            index += 1
            print("%d %s" % (index, music['music_name']))

        try:
            download_choice = input("请选择你要下载的歌曲[如：1，2，3或输入all全部下载]: ")
            if download_choice == "all":
                return musics_lists
            else:
                download_choice_list = download_choice.split(",")
                print("你选中的歌曲：")
                for download_index in download_choice_list:
                    music_info = musics_lists[int(download_index) - 1]
                    download_list.append(music_info)
                    print(music_info['music_name'])
                return download_list
        except Exception as e:
            print(e)

    def run(self):
        # 发送搜索歌曲请求
        params = {
            'keyword': self.search_music,
            'page': 1,
            'pagesize': 30,
            'platform': "WebFilter",
            # 'tag': "em",
            'iscorrection': 1
        }
        search_result = self.send_request(self.search_song, params)

        # 歌曲列表
        musics_list = self.handle_json_data(search_result, 1)

        # 把需要下载的歌曲加入到下载列表
        download_list = self.download_mange(musics_list)

        # hash = 718567D263C17BB3945B596CDD887C27 & album_id = 8308163 & _ = 1517146077031

        for music in download_list:
            params = {
                'hash': music['FileHash'],
                'album_id': music['AlbumID']
            }

            music_play = self.send_request(self.music_url, params)
            # 获取搜索出来的歌曲下载链接
            download_url_list = self.handle_json_data(music_play, 2)

            for download_url in download_url_list:
                # 下载歌曲
                music_name = music['music_name']
                music = self.send_request(download_url)
                self.download_music(music, music_name)


if __name__ == '__main__':
    search_music = input(u"请输入歌手或歌名：")
    kugou_music = KuGou(search_music)
    kugou_music.run()
