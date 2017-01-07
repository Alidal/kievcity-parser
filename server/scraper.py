import json
import asyncio
import aiohttp
from collections import namedtuple
from bs4 import BeautifulSoup

# It will cache all results to avoid pulling new information for every new user
CACHED_RESULTS = None

Project = namedtuple('Project', ['title', 'description', 'author', 'category',
                                 'goal', 'votes', 'link'])

async def get(url, params):
    response = await aiohttp.request('GET', url, params=params)
    return (await response.text())


class Scraper:
    data = []

    async def get_page(self, url, page_number):
        page = await get(url, params={'type': 3, 'page': page_number})
        soup = BeautifulSoup(page, 'html.parser')
        projects_list = soup.find_all(class_='project-card')
        cur_proj = {}
        if not projects_list:
            return

        for project in projects_list:
            cur_proj = {
                'category': project.a.span.string,
                'link': project.a.get('href'),
                'title': project.div.h1.a.string,
                'description': project.div.p.string,
                'author': project.div.select('.author')[0].select('.person')[0].span.string,
                'goal': project.div.select('.budget')[0].select('.sum')[0].string,
                'votes': project.div.select('.voted')[0].select('.total')[0].string,
            }
            self.data.append(cur_proj)

    async def scrape_website(self, url, app):
        global CACHED_RESULTS
        while True:
            # type=3 - 'На голосуваннi' state
            done, pending = await asyncio.wait([self.get_page(url, page_number)
                                               for page_number in range(50)])
            self.data = sorted(self.data, key=lambda item: int(item['votes']))

            CACHED_RESULTS = self.data
            for ws in app['websockets']:
                ws.send_str(json.dumps(self.data))
            asyncio.sleep(10)
