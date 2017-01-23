import asyncio
import aiohttp
from copy import copy
from bs4 import BeautifulSoup


KPI_PROJECTS_IDS = [573, 486, 344, 424, 336]


async def get(url):
    try:
        response = await aiohttp.request('GET', url)
    except:
        # If target website can't handle parsing
        return None, 502

    return await response.text(), response.status


class Scraper:
    def __init__(self, *args, **kwargs):
        self.cache = []
        # All possible project IDs, including not active
        self.active_projects_ids = list(range(700))

    def set_top(self):
        cur_sum = 0
        for i, _ in enumerate(self.cache):
            cur_sum += self.cache[i]['budget']
            self.cache[i]['is_top'] = cur_sum <= 50000000

    async def scrape_website(self, url, app):
        while True:
            self.current_data = []
            self.left_ids = copy(self.active_projects_ids)

            while self.left_ids:
                done, pending = await asyncio.wait(
                    [self.get_page(url, project_id)
                     for project_id in self.left_ids]
                )

            # Update cache only if all projects has been successfully parsed
            self.cache = sorted(self.current_data, reverse=True,
                                key=lambda item: int(item['votes']))
            self.set_top()
            print('Got {} fresh results.'.format(len(self.cache)))

            for ws in app['websockets']:
                ws.send_json(self.cache)

    async def get_page(self, url, project_id):
        project_url = url.format(project_id)
        page, status = await get(project_url)
        if status not in [200, 500]:
            return
        self.left_ids.remove(project_id)

        soup = BeautifulSoup(page, 'html.parser')
        # Get only active projects. If project is inactive or out of range of
        # possible ids - delete it from list
        if status == 500 or soup.find(class_='status').string != 'На голосуванні':
            self.active_projects_ids.remove(project_id)
            return

        cur_proj = {
            'author': soup.find(class_='author-presentation').get_text(strip=True),
            'budget': int(''.join(filter(str.isdigit, soup.find(class_='amount').strong.get_text()))),
            'category': soup.find(class_='category-tag').span.string,
            'description': soup.find(class_='desc').p.get_text(strip=True)[:300] + '...',
            'district': soup.find(class_='props').div.get_text().split()[3],
            'budget': int(''.join(filter(str.isdigit, soup.find(class_='amount').strong.get_text()))),
            'url': project_url,
            'title': soup.find('h1').get_text(strip=True)[:-14],
            'votes': soup.find(class_='supported').strong.get_text(),
            'is_kpi': project_id in KPI_PROJECTS_IDS,
        }
        self.current_data.append(cur_proj)
