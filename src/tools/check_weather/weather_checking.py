import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_weather_info(location_name):
    """
    Get current weather information for a given location using WeatherAPI.com
    
    Args:
        location_name (str): Name of the city/location
        
    Returns:
        dict: Weather information including temperature, description, humidity, etc.
    """
    API_KEY = os.getenv('WEATHER_API_KEY')  # Get your key from https://www.weatherapi.com/
    BASE_URL = "http://api.weatherapi.com/v1/current.json"
    
    if not API_KEY:
        return {'error': "API key not found. Please set WEATHER_API_KEY in your .env file"}
    
    params = {
        'key': API_KEY,
        'q': location_name,
        'aqi': 'no'  # Air quality info (optional)
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        weather_info = {
            'location': data['location']['name'],
            'country': data['location']['country'],
            'temperature': data['current']['temp_c'],
            'feels_like': data['current']['feelslike_c'],
            'description': data['current']['condition']['text'],
            'humidity': data['current']['humidity'],
            'wind_speed': data['current']['wind_kph'],
            'visibility': data['current']['vis_km'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return weather_info
        
    except requests.exceptions.RequestException as e:
        return {'error': f"Network error: {str(e)}"}
    except KeyError as e:
        return {'error': f"Data parsing error: {str(e)}"}
    except Exception as e:
        return {'error': f"Unexpected error: {str(e)}"}

# Test the function
if __name__ == "__main__":
    print("Testing WeatherAPI.com...")
    print("-" * 40)
    
    # Test with Melbourne
    info = get_weather_info("Melbourne")
    
    if 'error' in info:
        print(f"❌ Error: {info['error']}")
    else:
        print(f"🌤️  Weather in {info['location']}, {info['country']}:")
        print(f"🌡️  Temperature: {info['temperature']}°C (feels like {info['feels_like']}°C)")
        print(f"☁️  Description: {info['description']}")
        print(f"💧 Humidity: {info['humidity']}%")
        print(f"💨 Wind Speed: {info['wind_speed']} km/h")
        print(f"👁️  Visibility: {info['visibility']} km")
        print(f"⏰ Retrieved at: {info['timestamp']}")
    
    print("\n" + "-" * 40)
    print("✅ Test completed!")