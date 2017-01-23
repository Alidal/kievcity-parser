import jinja2
import asyncio
import argparse
import aiohttp_jinja2

from aiohttp import web
from server.scraper import Scraper

URL = 'https://gb.kievcity.gov.ua/projects/show/{}'

loop = asyncio.get_event_loop()


async def index(request):
    return aiohttp_jinja2.render_template('index.html', request, {})


async def on_shutdown(app):
    for ws in app['websockets']:
        await ws.close(code=999, message='Server shutdown')


async def start_background_tasks(app):
    scraper_instance = Scraper()
    app['scraper_instance'] = scraper_instance
    app['scraper'] = app.loop.create_task(scraper_instance.scrape_website(URL,
                                                                          app))


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    request.app['websockets'].append(ws)
    # Set start state
    ws.send_json(request.app['scraper_instance'].cache)

    # We don't need to handle any messages
    # from front-end part, so we just ignore it
    async for _ in ws:
        pass

    await ws.close()
    request.app['websockets'].remove(ws)
    return ws


async def init_app():
    app = web.Application(loop=loop)
    # Add handler for websockets
    app['websockets'] = []

    app.on_startup.append(start_background_tasks)
    app.on_shutdown.append(on_shutdown)
    app.router.add_get('/', index)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_static('/static', './client/dist')

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('./client/dist'))
    return app


parser = argparse.ArgumentParser(description='Parse set of URLs.')
parser.add_argument('--port', default=8080, type=int)

if __name__ == "__main__":
    args = parser.parse_args()

    app = loop.run_until_complete(init_app())
    web.run_app(app, port=args.port)
