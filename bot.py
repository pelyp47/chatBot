from aiogram import executor, types
from main_config import bot, dp
import asyncio
import websockets
import json
from database.database import User, Support, session

#set of connections of websockets
connections = {}

#websocket handle
async def server(websocket, path):
    while True:
        message = await websocket.recv()
        message = json.loads(message)
        connections[message["token"]] = websocket
        # Add a new user to the database
        if session.query(User).filter_by(token = message["token"]).first() is None:
            new_user = User(token=message["token"], name = message["title"], track_id = message["track_id"], support_id = session.query(Support).first().id)
            session.add(new_user)
            session.commit()
        await bot.send_message(session.query(User).filter_by(token = message["token"]).first().support_id, message["token"] + " " + message["message"])
      
start_server = websockets.serve(server, "localhost", 8765)


#handle start command
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if session.query(Support).filter_by(id = message.from_user.id).first() is None:
        new_support = Support(id = message.from_user.id, name = message.from_user.full_name)
        session.add(new_support)
        session.commit()
        print(f"support {message.from_user} was added")

#handle the support message
@dp.message_handler()
async def support_msg(message: types.Message):
    await message.reply(message.from_user)
    [token, messageContent] = [message.text.split(" ")[0], " ".join(message.text.split(" ")[1:])]
    data={"message": messageContent}
    client = connections[token]
    print(client)
    if client:
        # Send the data to the client
        await client.send(json.dumps(data))



#start all processes
asyncio.get_event_loop().run_until_complete(start_server)
executor.start_polling(dp)
asyncio.get_event_loop().run_forever()

