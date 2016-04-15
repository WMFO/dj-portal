from urllib import request
from lxml import html
import re

data = {
    "Signin[station]" : "wmfo",
    "Signin[email]" : "user@wmfo.org",
    "Signin[password]" : "password",
}

#spinitron_url = "https://spinitron.com/member/signin"

#urldata = parse.urlencode(data).encode('ascii')

#response = request.urlopen(spinitron_url,urldata)

#headers = dict(response.info())

#cookie = headers['Set-Cookie'].split(';')[0]

opener = request.build_opener()
opener.addheaders.append(('Cookie','SPINITRONSID=dqbtqva4t7ccg7sjkek5ltojo6'))
f = opener.open("https://spinitron.com/member/profileselect.php")
#f = opener.open("http://localhost:8080/test")
profiles = f.read()

root = html.fromstring(profiles)

for e in root.iter():
    if e.get("id") == 'profileselect':
        break


tr = e[0][1][0]
newUsers_html = tr[0]
editors_html = tr[1]
admins_html = tr[2]

tr = e[1][1][0]
users0 = tr[0]
users1 = tr[1]
users2 = tr[2]
users3 = tr[3]

def process_html(html_users, users):
    for user in html_users:
        if user.tag == 'a':
            uid = re.search("=([0-9]*)",user.get("href")).groups(0)[0]
            names = re.search("(.*) \((.*)\)", user.text).groups(0)
            email = user.get("title")
            users[email] = {
                'uid' : uid,
                'name' : names[0],
                'nickname' : names[1],
            }
    return users

users = process_html(users0,{})
users = process_html(users1,users)
users = process_html(users2,users)
users = process_html(users3,users)
admins = process_html(admins_html,{})
editors = process_html(editors_html,{})
newUsers = process_html(newUsers_html,{})

from dj_summary.models import SpinitronProfile



def store_users(users,permission):
    for k,v in users.items():
        sp = SpinitronProfile.objects.create(id=v['uid'])
        sp.spinitron_name = v['name']
        sp.dj_name = v['nickname']
        sp.spinitron_email = k
        sp.role = permission
        sp.save()

store_users(users,'U')
store_users(editors,'E')
store_users(admins,'A')
store_users(newUsers,'N')