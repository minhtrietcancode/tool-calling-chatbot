import os
from dotenv import load_dotenv
from openai import OpenAI

# Import the packages of 3 tools we have just created 
import src.tools.check_weather.weather_checking as check_weather
from src.tools.image_crawler.ImageCrawler import AutoCrawler
import src.tools.my_calculator.calculator as calculator 

# Load the API key for openrouter and weather api 
load_dotenv()
openai_api_key = os.getenv("OPENROUTER_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")


