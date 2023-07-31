from datetime import datetime
import requests
from celery.schedules import crontab
from django.contrib.auth.models import User
from django.core.mail import send_mail
from main.models import City, UserSubscriptions
from weatherreminder.celery import app
from django.conf import settings


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute=0, hour='*/1'),
        time_check.s()
    )


@app.task
def time_check():
    now = datetime.now().hour
    checked_cities = []
    sent = 0

    for user_subs in UserSubscriptions.objects.all():
        print(f'checking {User.objects.get(id=user_subs.user_id).username}')
        if not (user := User.objects.get(id=user_subs.user_id)).email:
            continue

        for subscription in user_subs.subscriptions.all():
            if now % subscription.notification_period == 0:
                sent += 1
                city_name = City.objects.get(id=subscription.city_id).name
                send_weather_info(user.email, city_name, city_name in checked_cities)
                checked_cities.append(city_name)

    return f"Sent {sent} emails"


def send_weather_info(email, city, is_city_checked):
    if is_city_checked:
        message = City.objects.get(name=city).current_weather
    else:
        api_url = "https://api.weatherbit.io/v2.0/current"
        api_key = settings.WEATHER_API_KEY
        lang = "UK"
        response = requests.get(api_url, params={"city": city, "key": api_key, "lang": lang})

        if response.status_code == 200:
            weather = response.json()['data'][0]
        else:
            return "error: Failed to fetch weather data"

        message = f"\nПогода в {city}:\n" \
                  f"Температура: {weather['temp']}°C\n" \
                  f"Відчувається як: {weather['app_temp']}°C\n" \
                  f"Тиск: {weather['pres']} mb.\n" \
                  f"Швидкість вітру: {weather['wind_spd']} м/с\n" \
                  f"Напрямок вітру: {weather['wind_cdir_full']}\n" \
                  f"Вологість повітря: {weather['rh']}%\n" \
                  f"Видимість: {weather['vis']}км\n" \
                  f"УФ-індекс: {weather['uv']}\n" \
                  f"Час останнього спостереження: {weather['ob_time']}"

        current_city = City.objects.get(name=city)
        current_city.current_weather = message
        current_city.save()

    send_mail(
        f"Погода в {city}",
        message,
        settings.EMAIL_HOST_USER,
        [email]
    )

    return 'Success'
