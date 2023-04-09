from aiogram import executor, types
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from main_config import bot, dp, owner_id
import pyperclip
import asyncio
import websockets
import json
import string
import secrets
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
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

        copyBtn = InlineKeyboardMarkup().add(InlineKeyboardButton(text = "copy token", callback_data = "token : "+message["token"]))
        await bot.send_message(session.query(User).filter_by(token = message["token"]).first().support_id, message["token"] + " " + message["message"], reply_markup = copyBtn)
        
      
start_server = websockets.serve(server, "localhost", 8765)



class Password(StatesGroup):
    waiting_for_password = State()

#handle start command
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state : FSMContext):
    if session.query(Support).filter_by(id = message.from_user.id).first() is None:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for i in range(12))
        await bot.send_message(owner_id, password + " " + message.from_user.full_name)
        await Password.waiting_for_password.set()
        await state.update_data(password = password)


@dp.message_handler(state=Password.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    password = data.get("password")
    print(password)
    if message.text == password:
        new_support = Support(id = message.from_user.id, name = message.from_user.full_name)
        session.add(new_support)
        session.commit()
        print(f"support {message.from_user} was added")
        await state.finish()
    else:
        await message.reply("wrong password")

@dp.callback_query_handler(lambda c: c.data.startswith('token : '))
async def copy_token(callback: CallbackQuery):
    token = callback.data.split(" : ")[1]
    pyperclip.copy(token)
    await callback.answer(f"token '{token}' was copied!")


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

