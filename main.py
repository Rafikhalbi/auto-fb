import requests, re, time
from bs4 import BeautifulSoup as bs

class Facebook:
    def __init__(self, cookies, head):
        self.head = head
        self.cookies = cookies
        
    def parsing(self, response):
        p = bs(response, "html.parser")
        return p
        
    def make_request(self, url):
        with requests.Session() as ses:
            language = ses.get(self.head.format("/language.php"), headers={"cookie": self.cookies})
            html = self.parsing(language.text)
            for link_language in html.find_all("form", method="post"):
                if "Indonesia" in str(link_language):
                    sl = self.head.format(link_language["action"])
                    fb_dtsg = link_language.find("input", attrs={"name": "fb_dtsg"})["value"]
                    jazoest = link_language.find("input", attrs={"name": "jazoest"})["value"]
            s = ses.post(sl, headers={"cookie": self.cookies}, data={"fb_dtsg": fb_dtsg, "jazoest": jazoest})
            response = ses.get(url, headers={"cookie": self.cookies})
            return response
    
    def information_account(self):
        response = self.make_request(self.head.format("/profile.php"))
        html = self.parsing(response.text)
        print(
                f"""
                *----> ACCOUNT INFORMATION
                (*) Name: {html.find("title").text}
                (*) UserId: {re.search(r'<input name="target" type="hidden" value="(.*?)"/>', str(html))[1]}
                """
            )
            
    def reaction_picker(self, url):
        response = self.make_request(url)
        html = self.parsing(response.text)
        for search in html.find_all("a"):
            if "Peduli" in str(search):
                care = self.head.format(search["href"])
        return care

    def get_comment(self, url):
        response = self.make_request(url)
        html = self.parsing(response.text)
        try:
            comment_link = self.head.format(html.find("form", {"method": "post"})["action"])
            fb_dtsg = html.find("input", {"type": "hidden", "name": "fb_dtsg"})["value"]
            jazoest = html.find("input", {"type": "hidden", "name": "jazoest"})["value"]
        except: pass
        return comment_link, fb_dtsg, jazoest

    def get_home(self, link):
        response = self.make_request(self.head.format("/home.php"))
        html = self.parsing(response.text)
        myclass = re.search(r'<\w+\s+class=\"([^\"]+)\" data-ft', str(html))[1]
        for page in html.find_all("div", attrs={"class": myclass}):
            user = page.find("strong").find("a").text
            try:
                tanggapi = self.reaction_picker(self.head.format(page.find("a", string="Tanggapi")["href"]))
                reg_comment = r'\bKomentar(i)?\b'
                comment = page.find("a", string=re.compile(reg_comment))["href"]
                if self.head.format("") in str(comment):
                    comment = comment
                else:
                    comment = self.head.format(comment)
                time.sleep(5)
                react = self.make_request(tanggapi)
                get_comment = self.get_comment(comment)[0]
                fb_dtsg = self.get_comment(comment)[1]
                jazoest = self.get_comment(comment)[2]
                data = {
                    "fb_dtsg": fb_dtsg,
                    "jazoest": jazoest,
                    "comment_text": f"Hello {user}👋"
                }
                post = requests.post(get_comment, headers={"cookie": self.cookies}, data=data)
                if react.status_code or post.status_code == 200:
                    print(f"name: {user}\nreaction: True | {react.status_code}\ncomment: True | {post.status_code}\ntext: Hello {user}👋\n", end="\r")
                else:
                    print(f"name: {user}\nreaction | {react.status_code}\ncomment: | {post.status_code}\n")
            except Exception as e:
                continue
        if "Lihat Berita Lain" in str(html):
            lbl = html.find("a", string="Lihat Berita Lain")["href"]
            self.get_home(link.format(lbl))
        else:
            self.get_home(self.head.format(""))
                
if __name__ == "__main__":
    cookies = open("cookies.txt", "r").read()
    head = "https://mbasic.facebook.com{}"
    try:
        fb = Facebook(cookies, head)
        fb.information_account()
    except Exception as e:
        exit("Please Login Cookies Before Use Script...")
    fb.get_home(head)
