import logging
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

BOT_TOKEN = "*********************************"
WEATHER_API_KEY = "**************************************"
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_weather(lat: float, lon: float) -> str:
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            city = data.get("name", "Неизвестное место")
            temp = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"]

            if temp <= 0:
                return f"📍 Город: {city}\n🌡 Температура: {int(temp) - 1}°C\n❄️ Холодно, одевайся теплее!\n🌥 {weather_desc.capitalize()}"
            elif 0 < temp < 15:
                return f"📍 Город: {city}\n🌡 Температура: {int(temp) + 1}°C\n☀️ Прохладно, но приятно!\n🌥 {weather_desc.capitalize()}"
            else:
                return f"📍 Город: {city}\n🌡 Температура: {int(temp) + 1}°C\n🔥 Жарко, выходи на прогулку!\n🌥 {weather_desc.capitalize()}"
        else:
            logger.error(f"Ошибка API OpenWeather: {data}")
            return "Не удалось получить данные о погоде. Попробуйте позже."

    except requests.RequestException as e:
        logger.error(f"Ошибка запроса к OpenWeather: {e}")
        return "Ошибка соединения с сервером погоды."


def get_weather_by_city(city: str) -> str:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            temp = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"]
            if temp <= 0:
                return f"📍Город {city}\n🌡 Температура: {int(temp) - 1}°C\n❄️ Советую одеться сегодня потеплее!\n🌥 {weather_desc.capitalize()}"
            if 0 < temp < 15:
                return f"📍Город {city}\n🌡 Температура: {int(temp) + 1}°C\n☀️ Сегодня хороший теплый день!\n🌥 {weather_desc.capitalize()}"
            else:
                return f"📍Город {city}\n🌡 Температура: {int(temp) + 1}°C\n🔥 Сегодня жарко, время идти гулять!\n🌥 {weather_desc.capitalize()}"

        else:
            return "Не удалось найти город. Проверьте правильность написания."

    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе к OpenWeather: {e}")
        return "Ошибка соединения с сервером погоды."


async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    first_name = user.first_name

    keyboard = [
        [KeyboardButton("📍 Отправить локацию", request_location=True)],
        [KeyboardButton("✏️ Ввести город")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Привет, {first_name}! Отправь свою локацию или введи свой город, и я расскажу тебе о погоде.",
        reply_markup=reply_markup,
    )


async def request_city(update: Update, context: CallbackContext) -> None:
    """Обработчик нажатия кнопки '✏️ Ввести город'. Запрашивает ввод города."""
    context.user_data["waiting_for_city"] = True  # Запоминаем, что пользователь хочет ввести город
    await update.message.reply_text("Введите название города, чтобы узнать погоду:")


async def handle_city(update: Update, context: CallbackContext) -> None:
    """Обработчик ввода города пользователем."""
    if context.user_data.get("waiting_for_city"):  # Проверяем, что бот ждет ввод города
        city = update.message.text
        weather_info = get_weather_by_city(city)
        context.user_data["waiting_for_city"] = False  # Сбрасываем флаг ожидания
        await update.message.reply_text(weather_info)
    else:
        await update.message.reply_text("Я не понимаю это сообщение. Используйте кнопки для взаимодействия.")


async def location(update: Update, context: CallbackContext) -> None:
    user_location = update.message.location
    if user_location:
        lat, lon = user_location.latitude, user_location.longitude
        weather_info = get_weather(lat, lon)
        await update.message.reply_text(weather_info)


def main() -> None:
    """Запуск бота."""
    app = Application.builder().token(BOT_TOKEN).build()

    # Обработчики команд и сообщений
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("✏️ Ввести город"), request_city))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city))
    app.add_handler(MessageHandler(filters.LOCATION, location))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_city))
    # Обрабатывает ввод города

    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
