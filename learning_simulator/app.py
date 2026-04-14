from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.responses import StreamingResponse
from fastapi import Response
from contextlib import asynccontextmanager

from server_class import Server
from observer_class import Observer

import asyncio
import uuid
import json

server = Server()
observer = Observer(server)

#  Code that runs on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(observer.message_listener())
    yield

app = FastAPI(lifespan=lifespan)
# load the static directory to the app (the app can use it directly)
app.mount("/static", StaticFiles(directory="static"), name="static")

# load first page = index.html 
@app.get("/")
async def root():
    return RedirectResponse("/static/index.html")

# used for Uptime robot ping
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.head("/health")
async def health_head():
    return Response(status_code=200)


# create WebSoclet endpoint (runs when a client opens the first page)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    while True:
        client_id = uuid.uuid4().hex[:8]
        if client_id not in server.connections.websockets:
            break

    await websocket.accept()
    server.connections.websockets[client_id] = websocket

    # send the first page as soon as the client connects
    await server.connections.change_page(client_id, "main_menu")

    try:
        while True:
            raw_msg = await websocket.receive_text()
            msg = json.loads(raw_msg)
            await server.message_queue.put((client_id, msg))
    except WebSocketDisconnect:
        await server.connections.disconnect(client_id)
    except Exception as e:
        print(f"Error: {e}")