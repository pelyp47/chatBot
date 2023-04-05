from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import CommandStart
import asyncio
import websockets
import json
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#bot config
TOKEN_API="6204898530:AAGobrG91GkYLfGVqCg3WSM__3XhLmsF2H8"
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

#set of connections of websockets
connections = {}

#database create and connect
engine = create_engine('sqlite:///database/data.db')
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    token = Column(String, primary_key = True)
    name = Column(String)
    track_id = Column(String)
    support_id = Column(Integer, ForeignKey("supports.id"))


class Support(Base):
    __tablename__ = "supports"
    id = Column(Integer, primary_key = True)
    name = Column(String)



Base.metadata.create_all(engine)

#session create
Session = sessionmaker(bind=engine)
session = Session()




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
async def echo(message: types.Message):
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

