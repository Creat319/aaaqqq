import requests
bcmc_id=input("请输入 bcmc 的作品 ID: ")
api_url=f"https://api-creation.codemao.cn/kitten/r2/work/player/load/{bcmc_id}"
try:
    response=requests.get(api_url)
    response.raise_for_status()
    print(response.text)
    response_data=response.json()
    target_url=None
    source_urls=response_data.get("source_urls")
    if source_urls:
        for url in source_urls:
            if isinstance(url,str) and url.endswith('.json'):
                target_url=url
                break
    if target_url:
        final_url=f"https://player.codemao.cn/new/179356903?bcmc_url={target_url}"
        print("\n"+final_url)
    else:
        print("\n666你输错作品编号了吧")
except requests.RequestException as req_err:
    print(f"你输错作品编号了，没有找到")
except ValueError as json_err:
    print(f"解析错误:{json_err}")
