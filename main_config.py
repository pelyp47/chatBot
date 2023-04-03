from aiogram import Bot, Dispatcher, executor, types
import asyncio
import websockets
import json
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#bot config
TOKEN_API="6204898530:AAGobrG91GkYLfGVqCg3WSM__3XhLmsF2H8"
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

#set of connections of websockets
connections = set()

#database create and connect
engine = create_engine('sqlite:///database/data.db')
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    token = Column(String, primary_key = True)
    name = Column(String)

Base.metadata.create_all(engine)

#session create
Session = sessionmaker(bind=engine)
session = Session()




#websocket handle
async def server(websocket, path):
    connections.add(websocket)
    while True:
        message = await websocket.recv()
        message = json.loads(message)
        await bot.send_message(1075894593, message["message"])
        # Add a new user to the database
        if session.query(User).filter_by(token = message["token"]).first() is None:
            new_user = User(token=message["token"], name = message["title"])
            session.add(new_user)
            session.commit()
        users = session.query(User).all()
        for user in users:
            print(user.token, user.name)
      
start_server = websockets.serve(server, "localhost", 8765)

#handle the support message
@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(message.from_user)
    data={"message": message.text}
    client = next(iter(connections), None)
    if client:
        # Send the data to the client
        await client.send(json.dumps(data))

#start all processes
asyncio.get_event_loop().run_until_complete(start_server)
executor.start_polling(dp)
asyncio.get_event_loop().run_forever()

