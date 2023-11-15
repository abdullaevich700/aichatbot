import logging
import openai
from telegram import ForceReply, Update, Location
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from geopy.geocoders import Nominatim
import requests
import os

openai.api_key = os.environ.get('openai.api_key')
openweathermap_api_key = os.environ.get('openweathermap_api_key')

geolocator = Nominatim(user_agent="Bot govt")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=False),
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.location:
        location = update.message.location
        latitude, longitude = location.latitude, location.longitude

        location_info = geolocator.reverse((latitude, longitude), language='en')
        location_address = location_info.address if location_info else "Location not found"

        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={openweathermap_api_key}"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        temperature = weather_data.get('main', {}).get('temp', 'Temperature not available')

        response_message = f"Location: {location_address}\nTemperature: {round(temperature - 273)}°C"

        await update.message.reply_text(response_message)

    else:
        user_message = update.message.text
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=user_message,
            max_tokens=100
        )
        bot_response = response['choices'][0]['text']
        await update.message.reply_text(bot_response)


def main() -> None:
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    application = Application.builder().token(os.environ.get('bot_token')).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.LOCATION, echo))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
