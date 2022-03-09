import requests

def main():
    headers = {
        'referer': 'https://howrare.is/api/v0.1/collections?__cf_chl_tk=jPS9qJiuiol.G6fqKhfDLMO16oRYUGmeYIZExvo7u6o-1646813331-0-gaNycGzNB_0',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    }

    url = 'https://howrare.is/api/v0.1/collections'

    response = requests.get(url, headers=headers)

    print(response.status_code)

main()