# OpenAI-tool-calling-demo
This script creates a chatbot using the OpenAI API to respond to user messages. It integrates custom functions for getting the current date and time, battery status, and live weather data for a specified location.

## Overview
The script creates a chatbot using the OpenAI API that can respond to user questions and call specific functions to retrieve real-time information. It supports three custom functions:

1. Get Current Date and Time: Returns the current date and time.
2. Get Battery Status: Reports the battery percentage and charging status.
3. Get Live Weather: Retrieves weather data for a specified location using the OpenWeatherMap API.

The chatbot runs in a loop, allowing the user to enter messages, which are processed by the OpenAI API. If a tool function is required, it is executed, and the result is shared with the user. The script keeps a short message history to maintain conversation context without exceeding the token limit.

The setup requires API keys for OpenAI and OpenWeatherMap, stored in an .env file, and installs necessary dependencies including `dotenv`, `openai`, `psutil`, and `requests`.

## Step-by-Step Setup
### 1. Dependencies
Python Libraries:

- dotenv: For loading environment variables.
- openai: OpenAI API library for making chat completions.
- datetime: To get the current date and time.
- psutil: To retrieve system information, such as battery status.
- requests: To make HTTP requests for fetching weather data.

Install Required Packages: Install these packages with pip if they’re not already installed:

```bash
pip install python-dotenv openai psutil requests
```

### 2. API Key Setup

Environment Variables:

Ensure you have an .env file named api.env in the same directory as the script with the following content:
```plaintext
OPENAI_API_KEY=your_openai_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
```

Replace `your_openai_api_key` and `your_openweather_api_key` with your actual OpenAI and OpenWeatherMap API keys.

Load Environment Variables: The script uses dotenv to load the API keys:

```python
load_dotenv("api.env")
```

## Example Usage
Run the script:

```bash
python chatbot.py
```

Interact with the bot by asking questions like:

"What is the current time?"
"What is the battery status?"
"What’s the weather in New York, US?"

## Script implementation details

### OpenAI Client initialization

```python
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
```

The client is initialized with the OpenAI API key to interact with OpenAI’s language models.

### Helper function definition

- `get_current_datetime()`: Returns the current date and time.
- `get_battery_status()`: Checks and returns the battery status using psutil. It will notify if battery information is unavailable.
- `get_live_weather(location)`: Fetches live weather data for a specified location using the OpenWeatherMap API.

The tools list defines the functions available to the chatbot, including descriptions, expected parameters, and function names:

```python
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
    ...
]
```

### Message Loop for User Interaction
The main loop lets users chat with the bot until they type "exit":

```python
while True:
    prompt = input("Enter a message (or type 'exit' to quit): ")
    if prompt.lower() == "exit":
        print("Ending chat session.")
        break
    ...
```

The script maintains a history of the last six messages to create a conversation context with the assistant.

### Maintaining Context in Message List

The script will prune old messages from the `message_list` object to prevent the token limit being exceeded, and all messages are appended with the appropriate role (e.g., `user`, `assistant`) to maintain context consistency.

### OpenAI Chat API Call
When a message is entered, it calls the OpenAI API with the message_list and tools to generate a response:

```python
completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=message_list,
    tool_choice="auto",
    tools=tools,
)
```

### Handling Tool Calls
If the model requests a tool, it’s called, and the result is printed and added to the conversation history:

```python
if tool_calls:
    for tool_call in tool_calls:
        function_called = tool_call.function.name
        function_args = tool_call.function.arguments
        function_args_json = json.loads(function_args)
        if function_called in globals():
            result = eval(f"{function_called}(**function_args_json)")
        ...
```

