import asyncio

class Observer:
    def __init__(self, server):
        self.server = server
        self.message_queue = server.message_queue

    async def message_listener(self):
        while True:
            client_id, msg = await self.message_queue.get()
            page_name = msg["page"]
            button = msg["button"]

            if page_name == "main_menu":
                if button == "japanese":
                    await self.server.join_japanese(client_id)
                elif button == "marines":
                    await self.server.join_marines(client_id)
                else:
                    print(f"{button} is not valid")

            elif page_name == "marines_menu":
                if button in ("marines_image", "marines_word", "marines_odd", "marines_category"):
                    await self.server.start_marines(client_id, button)
                else:
                    print(f"{button} is not valid")

            elif page_name == "word_selection":
                if button == "start":
                    await self.server.start_learning(client_id, msg["message"])
                else:
                    print(f"{button} is not valid")

            elif page_name == "learning":
                if button == "answer":
                    await self.server.handle_answer(client_id, msg["message"])
                else:
                    print(f"{button} is not valid")

            elif page_name == "stats":
                if button == "back":
                    await self.server.connections.change_page(client_id, "main_menu")
                else:
                    print(f"{button} is not valid")
            