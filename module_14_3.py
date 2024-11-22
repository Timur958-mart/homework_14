from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup, default_state
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from key_telegramm_bot import key
import asyncio

api = key
bot = Bot(token = api)
dp = Dispatcher(bot, storage = MemoryStorage())


start_menu = ReplyKeyboardMarkup(
    keyboard =[
        [KeyboardButton(text = 'Рассчитать'),
        KeyboardButton(text = 'Информация')]
], resize_keyboard = True
)
buy_button = KeyboardButton(text = 'Купить')
start_menu.add(buy_button)

kb = InlineKeyboardMarkup(
    inline_keyboard =[
        [InlineKeyboardButton(text = "Рассчитать норму калорий", callback_data = 'colories'),
        InlineKeyboardButton(text = "Формулы расчёта", callback_data = 'formulas')]
], resize_keyboard = True
)

product_menu = InlineKeyboardMarkup(
    inline_keyboard =[
        [InlineKeyboardButton(text = 'Продукт1', callback_data = 'product_buying'),
        InlineKeyboardButton(text = 'Продукт2', callback_data = 'product_buying'),
        InlineKeyboardButton(text = 'Продукт3', callback_data = 'product_buying'),
        InlineKeyboardButton(text = 'Продукт4', callback_data = 'product_buying')]
], resize_keyboard = True
)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(text = 'Рассчитать')
async def main_menu(message):
    await message.answer("Выберите опцию", reply_markup = kb)

@dp.callback_query_handler(text = 'formulas')
async def get_formulas(call):
    await call.message.answer(f"Формулы для расчёта нормы калорий:\n"
                              f"Женская формула: 10 х вес(кг) + 6,25 х рост(см) – 5 х возраст(г) – 161.\n"
                              f"Мужская формула: 10 х вес(кг) + 6,25 х рост(см) – 5 х возраст(г) + 5.")
    await call.answer()

@dp.callback_query_handler(text = 'colories')
async def set_age(call):
    await call.message.answer("Введите свой возраст в годах")
    await call.answer()
    await UserState.age.set()

@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    await state.update_data(age = message.text)
    await message.answer("Введите свой рост в сантиметрах")
    await UserState.growth.set()

@dp.message_handler(state = UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth = message.text)
    await message.answer("Введите свой вес в килограммах")
    await UserState.weight.set()

@dp.message_handler(state = UserState.weight)
async def send_colories(message, state):
    await state.update_data(weight = message.text)
    data = await state.get_data()
    calorie_allowance_man = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5
    calorie_allowance_woman = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161

    await message.answer(f"Ваша суточная норма калорий:\n"
                         f" для мужчин - {calorie_allowance_man} килокалорий,\n"
                         f" для женщин - {calorie_allowance_woman} килокалорий")
    await state.finish()

@dp.message_handler(text = 'Купить')
async def get_buying_list(message):
    for number in range(1, 5):
        await message.answer(f"Название: Product{number} | Описание: описание{number} | Цена: {number * 100}")
        with open(f'images/image{number}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer("Выберите продукт для покупки", reply_markup = product_menu)

@dp.callback_query_handler(text = 'product_buying')
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()

@dp.message_handler(commands = 'start')
async def start(message):
    await message.answer('Привет! Я бот, помогающий твоему здоровью.\n'
                         'Воспользуйтесь стартовым меню для начала работы',
                         reply_markup = start_menu)

@dp.message_handler()
async def all_messages(message):
    await message.answer("Введите команду /start, чтобы начать общение")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)
