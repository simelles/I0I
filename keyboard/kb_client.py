from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

k1 = KeyboardButton('Мои данные')
k2 = KeyboardButton('Параметры')
k3 = KeyboardButton('Анализ')
k4 = KeyboardButton('отмена')
k5 = KeyboardButton('Отчет')

start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(k2, k1)
params = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(k1)
cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(k4)
after = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(k3)
otch = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(k5)
