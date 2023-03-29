from aiogram import Bot, Dispatcher, executor, types
import asyncio
import websockets
import json

TOKEN_API="6204898530:AAGobrG91GkYLfGVqCg3WSM__3XhLmsF2H8"
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

connections = set()
# if __name__=="__main__":
#     executor.start_polling(dp)

async def server(websocket, path):
    connections.add(websocket)
    while True:
        message = await websocket.recv()
        await bot.send_message(1075894593, json.loads(message)["message"])
        
start_server = websockets.serve(server, "localhost", 8765)

@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(message.from_user)
    data={"message": message.text}
    client = next(iter(connections), None)
    if client:
        # Send the data to the client
        await client.send(json.dumps(data))
asyncio.get_event_loop().run_until_complete(start_server)
executor.start_polling(dp)
asyncio.get_event_loop().run_forever()

