import asyncio
# listen to the client actions(button presses) => tell the server what to do
class Observer:
    def __init__(self, server):
        self.server = server  #reference to the server
        self.message_queue = server.message_queue  # list of the client messages(actions) (html=>main.js=>app.py=>here)

    async def message_listener(self): # called on app launch (app.py)
        while True:
            client_id, msg = await self.message_queue.get() 
            page_name = msg["page"]
            button = msg["button"]

            # depending on the client action => tells the server what function to execute
            if page_name == "main_menu":
                if button == "japanese":
                    await self.server.join_japanese(client_id)
                else:
                    print(f"{button} is not valid")

            elif page_name == "word_selection":
                if button == "start":
                    selected = [
                        i for i, item in enumerate(msg["message"])
                        if item["selected"]
                    ]
                    await self.server.start_learning(client_id, selected)
                else:
                    print(f"{button} is not valid")
            
            elif page_name == "learning":
                if button == "answer":
                    await self.server.handle_answer(client_id, msg["message"])
                else:
                    print(f"{button} is not valid")