import asyncio
import os.path
import aioschedule as schedule
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType

from loader import dp, bot
from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from AI_check import check_csv, main, check_count
from keyboard import kb_client


class get(StatesGroup):
    file = State()


# @dp.register_message_handler(commands='start')
async def cmd_start(msg: types.Message):
    await msg.answer('*WARNING ALERT!!*\n'
                     'Этот бот показывает лишь некоторый функционал и не имеет ничего общего с конечным проектом.\n'
                     '', parse_mode="Markdown")
    await msg.answer('Привет, я бот от команды I0I, специально разработан для Axenix.'
                     '\nЯ создан для анализа и предсказаний burnout-ов у специалистов.'
                     '\nЯ работаю в 2-х режимах:'
                     '  \n1. Работаю с вашими данными(.csv). Данные должны соответсвовать моим параметрам.(нажмите Мои данные).'
                     '  \n2. Работаю с моими данными(для ознакомления).', reply_markup=kb_client.start)


# @dp.register_message_handler(commands='help')
async def cmd_help(msg: types.Message):
    await msg.answer('Связь с разработчиком - @simellesW\n'
                     'Кнопки:\n'
                     '/start - перезапуск бота\n'
                     '/myData - загрузка ваших данных, подогнанных под параметры\n'
                     '/params - параметры данных, с которыми умеет работать бот(не полный функционал)')


# @dp.register_message_handler(Text(equals='Мои данные'), state=None)
async def cmd_get(msg: types.Message):
    await msg.answer('Чтобы отменить - нажмите отмена\nЖду отправки ваших данных...', reply_markup=kb_client.cancel)
    await get.file.set()


# @dp.message_handler(state='*', commands='отмена')
# @dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cm_cancel(message: types.Message, state=FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('ок')


# @dp.register_message_handler(content_types=ContentType.ANY, State=get,file)
async def get_data(msg: types.Message, state: FSMContext):
    file_info = await bot.get_file(msg.document.file_id)
    print(file_info)
    for key, value in file_info :
        if key == 'file_path':
            if value[-3:] == 'csv':
                async with state.proxy() as data:
                    data['csv'] = msg.document.file_id
                downloaded_file = await bot.download_file(file_info.file_path)
                src = 'docs/' + msg.from_user.username + '.csv'
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file.read())
                a = check_csv(src)
                await msg.answer(a, reply_markup=kb_client.after)
                await state.finish()
            else:
                await msg.answer('Не тот тип файла')
                await state.finish()


# @dp.register_message_handler(Text(equals='Параметры'))
async def params(msg: types.Message):
    await msg.answer('Основные параметры датасета, на которых я обучался - это:'
                     '\nУникальный ID сотрудника'
                     '\nДата присоединения к компании'
                     '\nТип компании'
                     '\nВозможность выйти на удаленку'
                     '\nДолжность'
                     '\nУсилия сотрудника на работе'
                     '\nУсталость сотрудника(ментальное сотояние)', reply_markup=kb_client.params)


# @dp.register_message_handler(Text(equals='Анализ'))
async def anal(msg: types.Message):
    name = msg.from_user.username
    if os.path.isfile('docs/' + name + '.csv'):
        await msg.answer(f'Кол-во сотрудников, с наивысшим риском выгорания - {check_count("results/"+name)}')
        await msg.reply_document(open('results/' + name + '.csv', 'rb'))
    else:
        await msg.answer('Начинаю анализ, подождите...')
        main(name + '.csv')
        await msg.answer('Анализ завершен, вы автоматически подписались на ежедневную отправку отчета!')
        await msg.answer(f'Кол-во сотрудников, с наивысшим риском выгорания - {check_count("results/"+name)}')
        await msg.reply_document(open('results/' + name + '.csv', 'rb'))

# @dp.register_message_handler(Text(equals='Отчет'))
async def othcet(msg: types.Message):
    if os.path.isfile(f'docs/{msg.from_user.username + ".csv"}'):
        await bot.send_message('Отправляю вам отчет за сегодняшний день!')
        await msg.reply_document(open(f'results/{msg.from_user.username}'))
    else:
        await msg.answer('Вас еще нет в базе')


async def scheduler():
    schedule.every().day.at("22:00").do(othcet)
    while True:
        await schedule.run_pending()
        await asyncio.sleep(0.1)


def register_message_handler_client(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands='start')
    dp.register_message_handler(cmd_get, Text(equals='Мои данные'), state=None)
    dp.register_message_handler(cmd_get, commands='myData', state=None)
    dp.register_message_handler(cm_cancel, state='*', commands='cancel')
    dp.register_message_handler(cm_cancel, Text(equals='отмена', ignore_case=True), state='*')
    dp.register_message_handler(get_data, content_types=ContentType.ANY, state=get.file)
    dp.register_message_handler(params, Text(equals='Параметры'))
    dp.register_message_handler(params, commands='params')
    dp.register_message_handler(anal, Text(equals='Анализ'))
    dp.register_message_handler(othcet, Text(equals='Отчет'))
    dp.register_message_handler(cmd_help, commands='help')
