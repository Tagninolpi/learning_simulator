class Connections():
    def __init__(self):
        self.websockets = {}  # {"admin or player id": WS object} set in app.py
        self.connected = None  # None if empty, player_id if one player connected

    async def disconnect(self, client_id: str):
        if self.connected == client_id:
            self.connected = None
        websocket = self.websockets.pop(client_id, None)
        if websocket:
            try:
                print("disconnect")
                await websocket.close()
            except Exception as e:
                print(e)

    async def change_page(self, targets, new_page):
        if targets is None:
            target_ids = list(self.websockets.keys())
        elif isinstance(targets, str):
            target_ids = [targets]
        else:
            target_ids = list(targets)

        msg = {"type": "change_page", "payload": new_page}
        to_remove = []
        for client_id in target_ids:
            ws = self.websockets.get(client_id)
            if not ws:
                to_remove.append(client_id)
                continue
            try:
                await ws.send_json(msg)
            except Exception:
                to_remove.append(client_id)

        for client_id in to_remove:
            await self.disconnect(client_id)
    
    async def send_json(self, client_id: str, msg: dict):
        ws = self.websockets.get(client_id)
        if ws:
            try:
                await ws.send_json(msg)
            except Exception as e:
                print(e)
                await self.disconnect(client_id)