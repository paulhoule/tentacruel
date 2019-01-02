import re
from pathlib import Path
from urllib.parse import urljoin, unquote

from requests import get
import bs4

user_agent = "Kyubey/6.6.6 (there are spares but don't waste them)"
src="https://www.yumeost.club/2018/03/gintama-ost-download.html"
ending=src.split("/")[-1].replace(".html","")

link_pattern = re.compile("/[0-9]{4}/[0-2]{2}/[^/.]*[.]html")

output = Path.home() / "kyubey2" / ending
if not output.exists():
    output.mkdir(parents=True)

headers={"user-agent": user_agent}
response = get(src,headers=headers)
soup = bs4.BeautifulSoup(response.content,features="html.parser")
links = set()
for link in soup.find_all('a'):
    href = link.get('href')
    if href and link_pattern.match(href):
        links.add(urljoin(src,href))

MAX_CHUNK=100000
def tracked_download(from_url,to_path,headers=headers):
    with open(to_path,"wb") as destination:
        response = get(from_url, headers=headers, stream=True)
        for chunk in response.iter_content(MAX_CHUNK):
            print(".",end="",flush=True)
            destination.write(chunk)



for link in links:
    track_ending = link.split("/")[-1]
    response = get(link, headers=headers)
    soup = bs4.BeautifulSoup(response.content,features="html.parser")
    file_links = set()
    for inner_link in soup.find_all('iframe'):
        href = inner_link.get('src')
        if href and href.endswith('.html'):
            file_links.add(urljoin(link,href))

    for file in file_links:
        response = get(file, headers=headers)
        soup = bs4.BeautifulSoup(response.content, features="html.parser")
        for innermost_link in soup.select('div'):
            href = innermost_link.get('data-source')
            if href:
                print("mp3 at "+href)
                file_ending = track_ending.replace(".html",".mp3")
                output_file = output / file_ending
                if not output_file.exists():
                    print(f"Downloading {file_ending}")
                    tracked_download(href,output_file,headers)


