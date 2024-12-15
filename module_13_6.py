from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ":"
bot = Bot(token= api)
dp = Dispatcher(bot, storage= MemoryStorage())
kb = ReplyKeyboardMarkup()
but_1 = KeyboardButton(text= "Информация")
but_2 = KeyboardButton(text= 'Рассчитать')
kb.row(but_1, but_2)
kb.resize_keyboard = True

i_kb = InlineKeyboardMarkup()
i_but_1 = InlineKeyboardButton(text= "Рассчет калорий" , callback_data= 'calories')
i_but_2 = InlineKeyboardButton(text= "Формула расчета" , callback_data= 'formulas')
i_kb.row(i_but_1, i_but_2)

class UserState(StatesGroup):

    age = State()
    growth = State()
    weight = State()

def is_number(val):
    try:
        float(val)
        return True
    except ValueError:
        return False

@dp.message_handler(text = "Информация")
async def information(message):
    await message.answer('Мне пока нечего рассказать о себе, возможно я создан передавать масло')

@dp.message_handler(text= 'Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:' , reply_markup= i_kb)


@dp.callback_query_handler(text = "calories")
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()
    await call.answer()

@dp.callback_query_handler(text= 'formulas')
async def get_form(call):
    await call.message.answer("10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5")
    await call.answer()

@dp.message_handler(state= UserState.age)
async def set_growth(message, state):
    await state.update_data(age = message.text)
    data = await state.get_data()
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth= message.text)
    data = await state.get_data()
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state= UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight= message.text)
    data = await state.get_data()
    err = False

    if not is_number(data['weight']):
        await message.answer(f"{data['weight']}  не похоже на цифры, и как это посчитать???")
        err = True
        # await state.finish()
    if not is_number(data['age']):
        await message.answer(f"{data['age']}  не похоже на цифры, и как это посчитать???")
        err = True
        # await state.finish()
    if not is_number(data['growth']):
        await message.answer(f"{data['growth']}  не похоже на цифры, и как это посчитать???")
        err = True
        # await state.finish()
    if err:
        await state.finish()
        await message.answer("Попробуем еще раз??? " , reply_markup= kb)
    else:
        x_for_send = (float(data['weight'])*10) + (float(data['growth'])*6.25) - (float(data['age'])*5) - 5
        await message.answer(f'Ваша норма калорий {x_for_send}')
        await state.finish()
        await message.answer("Введите команду /start, чтобы начать общение.")

@dp.message_handler(commands= ['start'])
async def start_message(message):
    await message.answer("Привет! Я бот помогающий твоему здоровью", reply_markup= kb)

@dp.message_handler()
async def all_message(message):
    await message.answer("Введите команду /start, чтобы начать общение.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates= True)