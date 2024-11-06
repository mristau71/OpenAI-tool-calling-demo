from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
import psutil
import os, json, requests 

load_dotenv("api.env") 

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

def get_current_datetime():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery is None:
        return "Battery status not available on this device."

    percent = battery.percent
    plugged = battery.power_plugged
    status = "charging" if plugged else "discharging"

    return f"Battery is at {percent}% and currently {status}."

def get_live_weather(location):
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return "OpenWeatherMap API key is missing. Please set it in the environment."

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": location,
        "appid": api_key,
        "units": "imperial"
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return f"Error fetching weather data: {response.json().get('message', 'Unknown error')}"

    data = response.json()
    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]

    
    return (
        f"The current weather in {location} is {temp}°F with {description}. "
        f"Humidity is {humidity}%, and wind speed is {wind_speed} mph."
    )

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Returns the current date and time in the format 'YYYY-MM-DD HH:MM:SS'.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_battery_status",
            "description": "Returns the current battery percentage and charging status of the device.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_live_weather",
            "description": "Returns the current live weather information for a given location using the OpenWeatherMap API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city name and ISO 3166 country code, e.g., 'San Francisco, US'.",
                    }
                },
                "required": ["location"],
            },
        }
    }
]

# Create a list of messages to send to the API
message_list = [
    {
        "role": "system", 
        "content": "You are a helpful assistant."
    }
]

while True:
    prompt = input("Enter a message (or type 'exit' to quit): ")
    if prompt.lower() == "exit":
        print("Ending chat session.")
        break

    message_list.append({"role": "user", "content": prompt})

    if len(message_list) > 6:
        message_list = [message_list[0]] + message_list[-5:]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=message_list,
        tool_choice="auto",
        tools=tools,
    )

    answer = completion.choices[0].message.content
    tool_calls = completion.choices[0].message.tool_calls

    if tool_calls:
        for tool_call in tool_calls:
            function_called = tool_call.function.name
            function_args = tool_call.function.arguments
            function_args_json = json.loads(function_args)
            if function_called in globals():
                result = eval(f"{function_called}(**function_args_json)")
            else:
                result = "Function not found. Please try again."
            print(result)
            message_list.append({"role": "assistant", "content": result})
    else:
        print(answer)
        message_list.append({"role": "assistant", "content": answer})
