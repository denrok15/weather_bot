import logging
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

BOT_TOKEN = "**********************************"
WEATHER_API_KEY = "*************************"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def get_weather(lat: float, lon: float) -> str:
    if not WEATHER_API_KEY:
        return "Ошибка: не задан API-ключ погоды."

    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru"

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            city = data.get("name", "Неизвестное место")
            temp = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"]
            if temp <= 0:
                return f"📍Город {city}\n🌡 Температура: {temp}°C\n❄️ Советую одеться сегодня потеплее!\n🌥 {weather_desc.capitalize()}"
            if 0 < temp < 15:
                return f"📍Город {city}\n🌡 Температура: {temp}°C\n☀️ Сегодня хороший теплый день!\n🌥 {weather_desc.capitalize()}"
            else:
                return f"📍Город {city}\n🌡 Температура: {temp}°C\n🔥 Сегодня жарко, время идти гулять!\n🌥 {weather_desc.capitalize()}"




        else:
            logger.error(f"Ошибка API OpenWeather: {data}")
            return "Не удалось получить данные о погоде. Попробуйте позже."

    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе к OpenWeather: {e}")
        return "Ошибка соединения с сервером погоды."


async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    username = user.username
    first_name = user.first_name
    keyboard = [[KeyboardButton("📍 Отправить локацию", request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"Привет, {first_name}! Отправь свою локацию, и я расскажу тебе о погоде.", reply_markup=reply_markup
    )


async def location(update: Update, context: CallbackContext) -> None:
    user_location = update.message.location
    if user_location:
        lat, lon = user_location.latitude, user_location.longitude
        weather_info = get_weather(lat, lon)
        await update.message.reply_text(weather_info)


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.LOCATION, location))

    logger.info("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
