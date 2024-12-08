
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

API_KEY = '4ZbpI6ewuYqbjrGFtNsoZAvbOe4vMCQs'

# Функция для получения данных о погоде (AccuWeather API)
def get_weather_data(location_key):
    url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}?apikey={API_KEY}&details=true&metric=true"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None

# Функция для определения погодных условий
def check_bad_weather(weather_data):
    if weather_data:
        try:
            temperature = weather_data['DailyForecasts'][0]['Temperature']['Minimum']['Value']
            wind_speed = weather_data['DailyForecasts'][0]['Day']['Wind']['Speed']['Value']
            rain_probability = weather_data['DailyForecasts'][0]['Day']['RainProbability']

            if (temperature < 0 or temperature > 35) or \
               wind_speed > 50 or \
               rain_probability > 70:
                return "Ой-ой, погода плохая"
            else:
                return "Погода — супер"
        except (KeyError, IndexError): #Обработка отсутствия ключей в ответе API
            return "Неполные данные о погоде"
    else:
        return "Ошибка получения данных о погоде"


# Функция для получения location_key по названию города
def get_location_key(city_name):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={API_KEY}&q={city_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data and len(data) > 0:  # Проверяем, есть ли результаты поиска
            return data[0]['Key']
        else:
            return None  # Город не найден
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API поиска города: {e}")
        return None
    except (KeyError, IndexError):
        return None # Обработка некорректного ответа API


# Маршрут для главной страницы
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city1 = request.form.get('city1')
        city2 = request.form.get('city2')

        if not city1 or not city2:
            return "Ошибка: Оба поля города должны быть заполнены."

        location_key1 = get_location_key(city1)
        location_key2 = get_location_key(city2)

        if location_key1 and location_key2:
            weather_data1 = get_weather_data(location_key1)
            weather_data2 = get_weather_data(location_key2)

            weather_description1 = check_bad_weather(weather_data1)
            weather_description2 = check_bad_weather(weather_data2)

            return render_template('result.html', city1=city1, city2=city2,
                                   weather1=weather_description1, weather2=weather_description2)
        else:
            error_message = ""
            if not location_key1:
                error_message += f"Город '{city1}' не найден. "
            if not location_key2:
                error_message += f"Город '{city2}' не найден. "
            return f"Ошибка: {error_message}"

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)