# Intelligent Chatbot Assistant

## Overview/Objective

This project features an intelligent chatbot assistant designed to interact with users and leverage three distinct tools to provide information and perform tasks:

- **Calculator**: For performing various mathematical calculations.
- **Weather Checker**: For retrieving current weather information for specified locations.
- **Image Downloader**: For searching and downloading images from Google based on keywords.

You can see a video demonstration of the chatbot in action [here](https://drive.google.com/drive/folders/1h2UDMCoIFlXi9fVlWAVVUeen6Ryp_k_H?usp=sharing).

## Code Structure

The project follows a modular structure, with each tool encapsulated in its own directory within the `src/tools` folder.

```
tool-calling-chatbot/
├── main.py
├── pyproject.toml
├── README.md
├── src/
│   ├── tools/
│   │   ├── check_weather/
│   │   │   ├── __init__.py
│   │   │   └── weather_checking.py
│   │   ├── image_crawler/
│   │   │   ├── __init__.py
│   │   │   ├── collect_links.py
│   │   │   ├── ImageCrawler.py
│   │   │   └── requirements.txt
│   │   └── my_calculator/
│   │       ├── __init__.py
│   │       └── calculator.py
│   └── tool_calling_chatbot.egg-info/
└── uv.lock
```

### Module Descriptions:

-   **`main.py`**:
    -   This is the main entry point of the chatbot application.
    -   It initializes the `IntelligentChatbot` class, handles user input, analyzes messages to determine appropriate actions (tool usage, suggestions, clarifications, or conversational responses), and manages the display of chatbot interactions using `rich` for a visually appealing terminal UI.
    -   It integrates the three tools and orchestrates their execution based on user queries.

-   **`src/tools/`**:
    -   This directory contains the implementations of the various tools the chatbot can utilize.

-   **`src/tools/check_weather/`**:
    -   **`weather_checking.py`**: Contains the `get_weather_info` function, which uses the WeatherAPI.com to fetch current weather data for a given location. It handles API requests, parses responses, and returns structured weather information or error messages.

-   **`src/tools/image_crawler/`**:
    -   **`ImageCrawler.py`**: Implements the `AutoCrawler` class responsible for downloading images from Google. It uses `selenium` to interact with Google Images, handles image downloading, and ensures proper file saving and validation.
    -   **`collect_links.py`**: Provides the `CollectLinks` class, which is a dependency for `ImageCrawler.py`. It uses `selenium` (specifically `chromedriver`) to browse Google Images and collect image URLs based on keywords. It includes functionalities for scrolling, clicking, and handling various web elements to gather image links efficiently.
    -   **`requirements.txt`**: Lists the Python dependencies specific to the `image_crawler` tool (e.g., `selenium`, `webdriver-manager`, `Pillow`).

-   **`src/tools/my_calculator/`**:
    -   **`calculator.py`**: Defines the `calculator_tool` function, a simple calculator that evaluates mathematical expressions. It includes basic parsing, security checks to prevent malicious code execution, and handles common mathematical operations and errors like division by zero.

## Installation

This project uses `uv` for dependency management. Follow the steps below to set up your environment and install the necessary dependencies.

### 1. Install `uv`

If you don't have `uv` installed, you can install it using `pipx` (recommended) or `pip`:

**Using `pipx` (Recommended):**

```bash
pip install pipx
pipx ensurepath
pipx install uv
```

**Using `pip`:**

```bash
pip install uv
```

### 2. Install Dependencies

Navigate to the project's root directory and install the dependencies using `uv`:

```bash
uv sync
```

### 3. Set up API Keys

The weather tool requires an API key from [WeatherAPI.com](https://www.weatherapi.com/). The chatbot also uses OpenRouter.ai.

1.  Create a `.env` file in the root of your project.
2.  Add your API keys to the `.env` file as follows:

    ```
    WEATHER_API_KEY="your_weatherapi_key_here"
    OPENROUTER_API_KEY="your_openrouter_api_key_here"
    ```
    
## Usage Instructions

To run the chatbot, execute the following command from the project's root directory:

```bash
uv run python main.py
```

### Interaction:

-   The chatbot will greet you and display its available tools.
-   Type your messages and the chatbot will analyze them to decide whether to use a tool, suggest a tool, ask for clarification, or engage in normal conversation.
-   To exit the chat, type `quit`, `exit`, or `bye`.
