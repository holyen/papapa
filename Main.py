import requests
import re
import os
import threading
import socket

class Main:
    def __init__(self):
        self.torrent_path = 'torrent'
        self.not_proxies_ip=['119.28.83.206']
        self.header_data = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': '',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.t66y.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/59.0.3071.115 Safari/537.36',
        }
        if self.get_host_ip() not in self.not_proxies_ip:
            self.proxies = {
                'https': 'https://127.0.0.1:1087',
                'http': 'http://127.0.0.1:1087'
            }
        else:
            self.proxies= { }
        
        # if not exist torrent_dir, then create it
        if self.torrent_path not in os.listdir(os.getcwd()):
            os.makedirs(self.torrent_path)

    def get_host_ip(self):
        """
        查询本机ip地址
        :return: ip
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip


    def index_page(self, fid=2, page=1, downloadtype='wu'):
        p = re.compile("<h3><a href=\"(.+?)\"")
        try:
            tmp_url = "http://www.t66y.com/thread0806.php?fid=" + str(fid) + "&search=&page=" + str(page)
            r = requests.get(tmp_url, proxies=self.proxies)
            for i in p.findall(r.text):
                self.detail_page(i, page, downloadtype)

        except:
            print("index page " + str(page) + " get failed")

    def detail_page(self, url, page, downloadtype):
        p1 = re.compile("(http://rmdown.com/link.php.+?)<")
        p2 = re.compile("(http://www.rmdown.com/link.php.+?)<")
        base_url = "http://www.t66y.com/"
        try:
            r = requests.get(url=base_url + url, headers=self.header_data, proxies=self.proxies)
            url_set = set()
            for i in p1.findall(r.text):
                url_set.add(i)
            for i in p2.findall(r.text):
                url_set.add(i)
            url_list = list(url_set)
            for i in url_list:
                self.download_page(i, page, downloadtype)
        except:
            print("detail page " + url + " get failed")

    def download_page(self, url, page, downloadtype):
        header_data2 = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'rmdown.com',
            'Referer': 'http://www.viidii.info/?http://rmdown______com/link______php?' + url.split("?")[1],
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/59.0.3071.115 Safari/537.36'
        }
        try:
            download_text = requests.get(url, headers=header_data2).text
            p_ref = re.compile("name=\"ref\" value=\"(.+?)\"")
            p_reff = re.compile("NAME=\"reff\" value=\"(.+?)\"")
            ref = p_ref.findall(download_text)[0]
            reff = p_reff.findall(download_text)[0]
            r = requests.get("http://www.rmdown.com/download.php?ref=" + ref + "&reff=" + reff + "&submit=download")
            # just get green torrent link
            file_name = self.torrent_path + os.sep + downloadtype + os.sep + str(page) + os.sep + ref + ".torrent";
            if os.path.exists(file_name) is False:
                with open(file_name, "wb") as f:
                    f.write(r.content)
            else:
                print("download page " + url + " is exist")
        except:
            print("download page " + url + " failed")

    def start(self, downloadtype, page_start=1, page_end=10, max_thread_num=10):
        type_dict = {
            "asia": 2,
            "asia_code": 15,
            "e&a": 4,
            "anime": 5,
            "china": 25,
            "china_letter": 26,
        }

        # if not exist downloadtype_dir, then create it
        if downloadtype not in os.listdir(os.getcwd() + os.sep + self.torrent_path):
            os.makedirs(self.torrent_path + os.sep + downloadtype)

        if downloadtype in type_dict.keys():
            fid = type_dict[downloadtype]
        else:
            raise ValueError("type wrong!")
        max_thread_num = min(page_end - page_start + 1, max_thread_num)
        thread_list = []
        for page in range(page_start, page_end + 1):
            if str(page) not in os.listdir(os.getcwd() + os.sep + self.torrent_path + os.sep + downloadtype):
                os.makedirs(self.torrent_path + os.sep + downloadtype + os.sep + str(page))
            thread_list.append(threading.Thread(target=self.index_page, args=(fid, page, downloadtype)))
            # create thread to search page and download torrent
            # multi-thread in index page not download torrent, it's deliberate to avoid DDOS
        for t in range(len(thread_list)):
            thread_list[t].start()
            print("No." + str(t) + " thread start")
            while True:
                if len(threading.enumerate()) < max_thread_num:
                    break


if __name__ == "__main__":
    c = Main()
    c.start(downloadtype="china", page_start=1, page_end=200)
    c.start(downloadtype="asia", page_start=1, page_end=200)
    c.start(downloadtype="asia_code", page_start=1, page_end=200)
    c.start(downloadtype="china_letter", page_start=1, page_end=200)
