from pathlib import Path
from urllib.parse import urljoin, unquote

from requests import get
import bs4

user_agent = "Kyubey/4 (unlike Mozilla; Chrome sucks; I've got spares but please don't waste them)"
src="https://downloads.khinsider.com/game-soundtracks/album/hyperdimension-neptunia-duet-sisters-song-vol.2"
ending=src.split("/")[-1]

output = Path.home() / "kyubey" / ending
if not output.exists():
    output.mkdir(parents=True)

headers={"user-agent": user_agent}
response = get(src,headers=headers)
soup = bs4.BeautifulSoup(response.content,features="html.parser")
links = set()
for link in soup.find_all('a'):
    href = link.get('href')
    if href and href.endswith('.mp3'):
        links.add(urljoin(src,href))

links=list(links)
for link in links:
    response = get(link, headers=headers)
    soup = bs4.BeautifulSoup(response.content,features="html.parser")
    file_links = set()
    for inner_link in soup.find_all('a'):
        href = inner_link.get('href')
        if href and href.endswith('.mp3'):
            file_links.add(urljoin(link,href))

    for file in file_links:
        file_ending = unquote(file.split("/")[-1])
        output_file = output / file_ending
        if not output_file.exists():
            print(f"Downloading {file_ending}")
            response = get(file, headers=headers)
            output_file.write_bytes(response.content)


