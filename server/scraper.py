import json
import asyncio
import aiohttp
from bs4 import BeautifulSoup


async def get(url):
    response = await aiohttp.request('GET', url)
    if response.status == 200:
        return (await response.text())
    # If response code == 500
    response.close()
    # Return empty string for BeautifulSoup
    return ""


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Scraper(metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        # Cache for current state for not pulling new data for every new
        # WebSocket
        self.data = []
        self.cache = []
        # All possible project ids including not active
        self.active_projects_ids = list(range(700))

    async def get_page(self, url, project_number):
        page = await get(url.format(project_number))
        soup = BeautifulSoup(page, 'html.parser')
        # Get only active projects. If project is inactive or out of range of
        # possible ids - delete it from list
        if not page or soup.find(class_='status').string != 'На голосуванні':
            self.active_projects_ids.remove(project_number)
            return

        cur_proj = {
            'author': soup.find(class_='author-presentation').get_text(strip=True),
            'category': soup.find(class_='category-tag').span.string,
            'description': soup.find(class_='desc').p.get_text(strip=True)[:300] + '...',
            'district': soup.find(class_='props').div.get_text().split()[3],
            'budget': int(''.join(filter(str.isdigit, soup.find(class_='amount').strong.get_text()))),
            'link': url.format(project_number),
            'title': soup.find('h1').get_text(strip=True)[:-14],
            'votes': soup.find(class_='supported').strong.get_text(),
        }
        self.data.append(cur_proj)

    async def scrape_website(self, url, app):
        while True:
            self.cache = self.data
            self.data = []
            done, pending = await asyncio.wait([self.get_page(url, project_number)
                                               for project_number in self.active_projects_ids])

            # Update cache only if all projects has been successfully parsed
            if self.data:
                self.cache = sorted(self.data, reverse=True,
                                    key=lambda item: int(item['votes']))

            for ws in app['websockets']:
                ws.send_str(json.dumps(self.cache))
