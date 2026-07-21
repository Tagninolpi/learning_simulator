from connections_class import Connections
from game_class import Game
import asyncio
class Server:
    def __init__(self):
        self.message_queue = asyncio.Queue()
        self.connections = Connections()
        self.game = Game()

    async def join_japanese(self, client_id):
        if not self.connections.connected:
            self.connections.connected = client_id
            await self.connections.change_page(client_id, "word_selection")
            await asyncio.sleep(0.3)
            payload = [
                {"japanese": jp, "german": de}
                for jp, de in self.game.all_words
            ]
            await self.connections.send_json(client_id, {
                "type": "set_buttons",
                "payload": payload
            })

    async def start_learning(self, client_id, selected_indices: list):
        self.game.set_active_words_from_indices(selected_indices)
        self.connections.connected = None
        await self.connections.change_page(client_id, "learning")
        await asyncio.sleep(0.3)
        await self._send_question(client_id)

    async def handle_answer(self, client_id, was_correct: bool):
        self.game.answer(was_correct)
        question = self.game.next_question()
        if question is None:
            # all words guessed correctly — reset and go back to menu
            self.game.active_words = []
            await self.connections.change_page(client_id, "main_menu")
        else:
            await self.connections.send_json(client_id, {
                "type": "question",
                "payload": question
            })

    async def _send_question(self, client_id):
        question = self.game.next_question()
        if question:
            await self.connections.send_json(client_id, {
                "type": "question",
                "payload": question
            })