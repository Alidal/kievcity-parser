import json
import jinja2
import asyncio
import aiohttp_jinja2

from aiohttp import web, WSMsgType
from server.scraper import Scraper

URL = 'https://gb.kievcity.gov.ua/projects/show/{}'

loop = asyncio.get_event_loop()


async def index(request):
    return aiohttp_jinja2.render_template('index.html', request, {})


async def on_shutdown(app):
    for ws in app['websockets']:
        await ws.close(code=999, message='Server shutdown')


async def start_background_tasks(app):
    app['scraper'] = app.loop.create_task(Scraper().scrape_website(URL, app))


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    if ws not in request.app['websockets']:
        request.app['websockets'].append(ws)

    # Set start state
    ws.send_str(json.dumps(Scraper().cache))
    return ws


async def init():
    app = web.Application(loop=loop)
    # We will handle websockets in app
    app['websockets'] = []

    app.on_startup.append(start_background_tasks)
    app.on_shutdown.append(on_shutdown)
    app.router.add_get('/', index)
    app.router.add_get('/ws', websocket_handler)
    app.router.add_static('/static', './client/static')

    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('./client/templates'))
    return app


if __name__ == "__main__":
    app = loop.run_until_complete(init())
    web.run_app(app)
