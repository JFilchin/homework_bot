# Homework Bot

## О проекте

Что делает Homework Bot:
+ раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверет статус отправленной на ревью домашней работы;
+ при обновлении статуса анализирует ответ API и отправляет вам соответствующее уведомление в Telegram;
+ логирует свою работу и сообщает вам о важных проблемах сообщением в Telegram.

## Стек технологий
![Python](https://img.shields.io/badge/-Python-black?style=for-the-badge&logo=python)
![Telegram API](https://img.shields.io/badge/-python_telegram_bot-black?style=for-the-badge&logo=telegram)


## Инструкция
Чтобы развернуть проект локально, необходимо склонировать репозиторий себе на компьютер:

```bash
git clone <название репозитория>
```

```bash
cd <название репозитория> 
```

Cоздать и активировать виртуальное окружение:

*Для Windows:*
```bash
python -m venv venv
source venv/Script/activate
```
*Для Linux/MacOS:*
```bash
python3 -m venv venv
source venv/bin/activate
```

Создать файл .env по образцу ".env.example":

```bash
touch .env
```

Установить зависимости из файла requirements.txt:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

