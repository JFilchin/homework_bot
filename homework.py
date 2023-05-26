import os
import sys
import time
import logging
import requests

import telegram

from http import HTTPStatus

from dotenv import load_dotenv

from exceptions import SendMessageError, GetApiAnswerError

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.DEBUG)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = os.getenv('ENDPOINT')
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Функция проверяет доступность переменных окружения."""
    if not PRACTICUM_TOKEN:
        logging.error('Нет токена PRACTICUM_TOKEN')
    if not TELEGRAM_TOKEN:
        logging.error('Нет токена TELEGRAM_TOKEN')
    if not TELEGRAM_CHAT_ID:
        logging.error('Нет токена TELEGRAM_CHAT_ID')
    if all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)):
        logging.debug('Успешно. Все необходимые токены получены\n')
        return None
    logging.critical('Приостанавливаем программу')
    sys.exit('Ошибка. Отсутствуют переменные окружения.')


def send_message(bot, message):
    """Функция отправляет сообщение в Telegram чат.
    Чат определяется переменной окружения TELEGRAM_CHAT_ID.
    """
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug(f'Отправлено сообщение:\n\'{message}\'\n')
    except telegram.error.TelegramError as error:
        logging.error(f'Ошибка при отправке сообщения: {error}')
        raise SendMessageError(f'Ошибка при отправке сообщения: {error}')


def get_api_answer(timestamp):
    """Функция делает запрос к эндпоинту API-сервиса.
    В качестве параметра в функцию передается временная метка.
    В случае успешного запроса должна вернуть ответ API,
    приведя его из формата JSON к типам данных Python.
    """
    payload = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params=payload
        )
        response.raise_for_status()
        logging.debug(f'Успешно. Запрос к API: {ENDPOINT}.\n')
        if response.status_code != HTTPStatus.OK:
            response_error = (
                'Ошибка при запросе к API. {status}, {text}'.format(
                    status=response.status_code,
                    text=response.text,
                ))
            logging.error(response_error)
            raise requests.HTTPError(response_error)
    except requests.RequestException as error:
        response_error = (
            f'Ошибка при запросе к {ENDPOINT}.\nОшибка: {error}\n'
        )
        logging.error(response_error)
        raise GetApiAnswerError(response_error)
    return response.json()


def check_response(response):
    """Функция проверяет ответ API.
    Она должна соответствовать документации из урока по API
    сервиса Практикум.Домашка.
    """
    if not response:
        answer_API = 'Ошибка. Ответ API содержит пустой словарь.'
        logging.error(answer_API)
        raise KeyError(answer_API)
    if not isinstance(response, dict):
        answer_API = 'Ошибка. Ответ API имеет некорректный тип.'
        logging.error(answer_API)
        raise TypeError(answer_API)
    if 'homeworks' not in response:
        answer_API = 'Ошибка. Отсутствует необходимый ключ в ответе.'
        logging.error(answer_API)
        raise KeyError(answer_API)
    if not isinstance(response["homeworks"], list):
        answer_API = (
            'Ошибка. В ответе API неверный тип данных у элемента homeworks'
        )
        logging.error(answer_API)
        raise TypeError(answer_API)
    return response['homeworks']


def parse_status(homework):
    """Функция извлекает статус последней отправленной домашней работы.
    Возвращает статус этой работы и один из вердиктов словаря
    HOMEWORK_VERDICTS.
    """
    for key in ('homework_name', 'status'):
        if key not in homework:
            key_error = (
                'Ошибка. Отсутствует необходимый ключ для определения статуса '
                f'проверки домашнего задания: {key}'
            )
            logging.error(key_error)
            raise KeyError(key_error)

    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        homework_status_error = (
            'Ошибка. Не совпадает название статуса проверки '
            f'домашней работы: {homework_status}'
        )
        logging.error(homework_status_error)
        raise KeyError(homework_status_error)
    verdict = HOMEWORK_VERDICTS[homework_status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()  # Проверяем наличие токенов
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    # timestamp = 1549962000
    timestamp = int(time.time())
    homework_status_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                status_homework = parse_status(homeworks[0])
                if status_homework not in homework_status_message:
                    homework_status_message = status_homework
                    send_message(bot, homework_status_message)
        except Exception as error:
            message = f'Ошибка. Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            logging.debug(f'Пауза на {int(RETRY_PERIOD/60)} минут')
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
