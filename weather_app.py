from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    try:
        data = request.get_json()
        city = data.get('city')
        
        if not city:
            return jsonify({'error': 'Nazwa miasta jest wymagana'}), 400
        
        params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric',
            'lang': 'pl'
        }
        
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code == 404:
            return jsonify({'error': 'Miasto nie zostało znalezione'}), 404
        elif response.status_code != 200:
            return jsonify({'error': 'Błąd podczas pobierania danych pogodowych'}), 500
        
        weather_data = response.json()
        forecast_response = requests.get(FORECAST_URL, params=params)
        forecast_data = forecast_response.json() if forecast_response.status_code == 200 else None
        
        current_weather = {
            'city': weather_data['name'],
            'country': weather_data['sys']['country'],
            'temperature': round(weather_data['main']['temp']),
            'feels_like': round(weather_data['main']['feels_like']),
            'description': weather_data['weather'][0]['description'].capitalize(),
            'icon': weather_data['weather'][0]['icon'],
            'humidity': weather_data['main']['humidity'],
            'pressure': weather_data['main']['pressure'],
            'wind_speed': weather_data['wind']['speed'],
            'wind_direction': weather_data['wind'].get('deg', 0),
            'visibility': weather_data.get('visibility', 0) / 1000,
            'sunrise': datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M')
        }
        
        forecast = []
        if forecast_data:
            daily_forecasts = {}
            for item in forecast_data['list'][:15]:
                date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                if date not in daily_forecasts:
                    daily_forecasts[date] = {
                        'date': datetime.fromtimestamp(item['dt']).strftime('%d.%m'),
                        'day_name': datetime.fromtimestamp(item['dt']).strftime('%A'),
                        'temperature': round(item['main']['temp']),
                        'description': item['weather'][0]['description'].capitalize(),
                        'icon': item['weather'][0]['icon'],
                        'humidity': item['main']['humidity']
                    }
            forecast = list(daily_forecasts.values())[:5]
        
        return jsonify({
            'current': current_weather,
            'forecast': forecast
        })
        
    except Exception as e:
        return jsonify({'error': f'Wystąpił błąd: {str(e)}'}), 500

@app.route('/weather/coordinates', methods=['POST'])
def get_weather_by_coordinates():
    try:
        data = request.get_json()
        lat = data.get('lat')
        lon = data.get('lon')
        
        if not lat or not lon:
            return jsonify({'error': 'Współrzędne są wymagane'}), 400
        
        params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': 'metric',
            'lang': 'pl'
        }
        
        response = requests.get(BASE_URL, params=params)
        
        if response.status_code != 200:
            return jsonify({'error': 'Błąd podczas pobierania danych pogodowych'}), 500
        
        weather_data = response.json()
        
        current_weather = {
            'city': weather_data['name'],
            'country': weather_data['sys']['country'],
            'temperature': round(weather_data['main']['temp']),
            'feels_like': round(weather_data['main']['feels_like']),
            'description': weather_data['weather'][0]['description'].capitalize(),
            'icon': weather_data['weather'][0]['icon'],
            'humidity': weather_data['main']['humidity'],
            'pressure': weather_data['main']['pressure'],
            'wind_speed': weather_data['wind']['speed'],
            'wind_direction': weather_data['wind'].get('deg', 0),
            'visibility': weather_data.get('visibility', 0) / 1000,
            'sunrise': datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M'),
            'sunset': datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M')
        }
        
        return jsonify({'current': current_weather})
        
    except Exception as e:
        return jsonify({'error': f'Wystąpił błąd: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)