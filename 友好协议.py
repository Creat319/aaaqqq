from bs4 import BeautifulSoup
import json
from json import dumps
import requests

headers = {
    "Content-Type": "application/json",
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17'
}


def get_pid():
    res = requests.get('https://shequ.codemao.cn', headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    data = json.loads(soup.find_all("script")[0].string.split("=")[1])
    return data['pid']


def login(identity, password):
    login_url = 'https://api.codemao.cn/tiger/v3/web/accounts/login'
    login_data = {
        'identity': identity,
        'password': password,
        'pid': get_pid()
    }
    response = requests.post(
        login_url, headers=headers, data=dumps(login_data))
    response_data = json.loads(response.text)
    if 'auth' not in response_data:
        print("1:", response.text)
        return None, None
    authorization = response_data['auth']['token']
    cookies = response.cookies.get_dict()
    return authorization, cookies


def sign_friendly_agreement(authorization, cookies):
    sign_url = 'https://api.codemao.cn/nemo/v3/user/level/signature'
    sign_headers = headers.copy()
    sign_headers['authorization'] = authorization
    response = requests.post(sign_url, headers=sign_headers, cookies=cookies)
    if response.status_code == 200:
        print("成功")
    else:
        print("失败:", response.text)


def main():
    identity = input('账号: ')
    password = input('密码: ')
    authorization, cookies = login(identity, password)
    if authorization and cookies:
        print("loading..")
        sign_friendly_agreement(authorization, cookies)
    else:
        print("0")


if __name__ == '__main__':
    main()
