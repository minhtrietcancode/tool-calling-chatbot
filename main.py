import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Rich imports for beautiful terminal UI
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns
from rich.align import Align
from rich.table import Table
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

# Import the packages of 3 tools we have just created 
import src.tools.check_weather.weather_checking as check_weather
from src.tools.image_crawler.ImageCrawler import AutoCrawler
import src.tools.my_calculator.calculator as calculator 

# Load the API key getting from openrouter
load_dotenv()
openai_api_key = os.getenv("OPENROUTER_API_KEY")

# Initialize Rich console
console = Console()

class IntelligentChatbot:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openai_api_key,
        )
        self.conversation_history = []
        self.pending_action = None  # Store pending tool suggestions
        
        # Initialize image crawler
        self.image_crawler = AutoCrawler(
            download_path='downloaded_images',
            full_resolution=False,
            no_gui=True
        )
    
    def analyze_message(self, user_message):
        """Step 1: Analyze user message and decide what action to take"""
        
        system_prompt = """You are an intelligent assistant that can use 3 tools:

1. CALCULATOR: For math calculations - you MUST convert natural language math questions into proper mathematical expressions
2. WEATHER: For weather information - needs a city name
3. IMAGE_DOWNLOADER: For downloading images from Google - needs a keyword and count

IMPORTANT FOR CALCULATOR: When users ask math questions in natural language, you MUST convert them to proper mathematical expressions:
- "989 times with 9909" → "989 * 9909"
- "what is 50 plus 25" → "50 + 25"
- "divide 100 by 4" → "100 / 4"
- "5 to the power of 3" → "5 ** 3"
- "square root of 16" → "16 ** 0.5"
- "what's 15 minus 8" → "15 - 8"

Your job is to analyze the user's message and decide what to do. Respond with ONLY a JSON object:

For direct tool use (when user clearly wants calculation/weather/images):
{"action": "use_tool", "tool": "calculator", "params": {"expression": "989 * 9909"}}
{"action": "use_tool", "tool": "weather", "params": {"location": "Melbourne"}}
{"action": "use_tool", "tool": "images", "params": {"keyword": "cats", "count": 5}}

For suggesting tools (when user mentions something that could use a tool):
{"action": "suggest_tool", "tool": "images", "suggestion": "Would you like me to download some cat pictures?"}

For asking clarification (when tool info is missing):
{"action": "ask_clarification", "tool": "weather", "question": "What city would you like weather information for?"}
{"action": "ask_clarification", "tool": "images", "question": "How many pictures would you like me to download?"}

For normal chat (no tools needed):
{"action": "chat", "response": "Your normal conversational response here"}

Math question examples:
- "What's 5 + 3?" → {"action": "use_tool", "tool": "calculator", "params": {"expression": "5 + 3"}}
- "989 times with 9909" → {"action": "use_tool", "tool": "calculator", "params": {"expression": "989 * 9909"}}
- "What is the result of 50 divided by 2?" → {"action": "use_tool", "tool": "calculator", "params": {"expression": "50 / 2"}}
- "Calculate 15 plus 25 minus 10" → {"action": "use_tool", "tool": "calculator", "params": {"expression": "15 + 25 - 10"}}

Weather examples:
- "Weather in Tokyo" → use weather directly  
- "What's the weather?" → ask for city

Image examples:
- "Download 10 cat images" → use images directly
- "I love dogs" → suggest images
- "Download some pictures" → ask for keyword and count

Chat examples:
- "How are you?" → normal chat
- "Tell me a joke" → normal chat
"""

        try:
            # Show thinking spinner
            with console.status("[bold green]🤔 Thinking...", spinner="dots"):
                response = self.client.chat.completions.create(
                    model="qwen/qwen2.5-vl-32b-instruct:free",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.1
                )
            
            analysis = response.choices[0].message.content.strip()
            return json.loads(analysis)
            
        except Exception as e:
            console.print(f"[red]Error in analysis: {e}[/red]")
            return {"action": "chat", "response": "Sorry, I had trouble understanding that. Could you try again?"}
    
    def execute_tool(self, tool, params):
        """Execute the specified tool with given parameters"""
        
        try:
            if tool == "calculator":
                with console.status(f"[bold blue]🧮 Calculating {params['expression']}...", spinner="dots"):
                    result = calculator.calculator_tool(params["expression"])
                
                if result["error"]:
                    return f"Sorry, I couldn't calculate that: {result['error']}"
                else:
                    return f"The answer is: {result['result']}"
            
            elif tool == "weather":
                with console.status(f"[bold cyan]🌤️ Getting weather for {params['location']}...", spinner="weather"):
                    result = check_weather.get_weather_info(params["location"])
                
                if "error" in result:
                    return f"Sorry, I couldn't get weather info: {result['error']}"
                else:
                    # Create a beautiful weather table
                    weather_table = Table(show_header=False, box=None, padding=(0, 1))
                    weather_table.add_column("Icon", style="bold")
                    weather_table.add_column("Info", style="")
                    
                    weather_table.add_row("🌍", f"[bold]{result['location']}, {result['country']}[/bold]")
                    weather_table.add_row("🌡️", f"Temperature: [bold cyan]{result['temperature']}°C[/bold cyan] (feels like {result['feels_like']}°C)")
                    weather_table.add_row("☁️", f"Conditions: [bold yellow]{result['description']}[/bold yellow]")
                    weather_table.add_row("💧", f"Humidity: [bold blue]{result['humidity']}%[/bold blue]")
                    weather_table.add_row("🌬️", f"Wind: [bold green]{result['wind_speed']} km/h[/bold green]")
                    weather_table.add_row("👁️", f"Visibility: [bold magenta]{result['visibility']} km[/bold magenta]")
                    
                    return weather_table
            
            elif tool == "images":
                keyword = params["keyword"]
                count = params.get("count", 5)
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task(f"🖼️ Downloading {count} images of '{keyword}'...", total=None)
                    success = self.image_crawler.download_keyword_images(keyword, count)
                
                if success:
                    return f"✅ Successfully downloaded [bold green]{count}[/bold green] images of '[bold cyan]{keyword}[/bold cyan]'! Check the 'downloaded_images/{keyword}/' folder."
                else:
                    return f"❌ Sorry, I couldn't download images of '{keyword}' right now."
        
        except Exception as e:
            return f"❌ Sorry, I'm currently unavailable for this request."
    
    def generate_response(self, user_message, tool_result=None):
        """Step 2: Generate natural response, optionally including tool results"""
        
        context = f"User said: {user_message}"
        if tool_result:
            context += f"\nTool result: {tool_result}"
            system_prompt = "You are a friendly chatbot. The user asked something and you used a tool to help them. Respond naturally and conversationally, incorporating the tool result into your response."
        else:
            system_prompt = "You are a friendly chatbot. Respond naturally and conversationally to the user's message."
        
        try:
            with console.status("[bold green]✨ Generating response...", spinner="dots"):
                response = self.client.chat.completions.create(
                    model="qwen/qwen2.5-vl-32b-instruct:free",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": context}
                    ],
                    temperature=0.7
                )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return "Sorry, I'm having trouble responding right now."
    
    def chat(self, user_message):
        """Main chat function that handles the complete flow"""
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Step 1: Analyze the message
        analysis = self.analyze_message(user_message)
        
        # Handle different actions
        if analysis["action"] == "use_tool":
            # Execute tool directly
            tool_result = self.execute_tool(analysis["tool"], analysis["params"])
            
            # If tool_result is a Table (weather), display it directly
            if hasattr(tool_result, 'add_row'):
                return tool_result
            else:
                response = self.generate_response(user_message, tool_result)
                return response
            
        elif analysis["action"] == "suggest_tool":
            # Suggest using a tool
            response = analysis["suggestion"]
            self.pending_action = {"tool": analysis["tool"], "keyword": self.extract_keyword_from_message(user_message)}
            return response
            
        elif analysis["action"] == "ask_clarification":
            # Ask for missing information
            response = analysis["question"]
            self.pending_action = {"tool": analysis["tool"], "waiting_for": "clarification"}
            return response
            
        else:
            # Normal chat
            response = analysis["response"]
            return response
    
    def handle_pending_action(self, user_response):
        """Handle responses to tool suggestions or clarification requests"""
        
        if not self.pending_action:
            return self.chat(user_response)
        
        pending = self.pending_action
        self.pending_action = None  # Clear pending action
        
        # Handle tool suggestions (yes/no responses)
        if "tool" in pending and "keyword" in pending:
            if any(word in user_response.lower() for word in ["yes", "yeah", "sure", "ok", "please"]):
                if pending["tool"] == "images":
                    # Ask for count if not specified
                    try:
                        count = int(''.join(filter(str.isdigit, user_response)))
                        if count == 0:
                            raise ValueError
                    except:
                        return "How many pictures would you like me to download?"
                    
                    tool_result = self.execute_tool("images", {"keyword": pending["keyword"], "count": count})
                    return self.generate_response(f"download {count} {pending['keyword']} images", tool_result)
            else:
                return "No problem! Is there anything else I can help you with?"
        
        # Handle clarification responses
        elif "waiting_for" in pending:
            if pending["tool"] == "weather":
                # User provided city name
                tool_result = self.execute_tool("weather", {"location": user_response})
                return tool_result  # Return the table directly
            
            elif pending["tool"] == "images":
                # This could be keyword or count - analyze the response
                return self.chat(f"download images of {user_response}")
        
        # Fallback to normal chat
        return self.chat(user_response)
    
    def extract_keyword_from_message(self, message):
        """Extract potential image keyword from user message"""
        # Simple keyword extraction - could be improved
        words = message.lower().split()
        # Remove common words
        common_words = {"i", "love", "like", "hate", "the", "a", "an", "and", "or", "but", "is", "are", "was", "were"}
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        return keywords[-1] if keywords else "images"

def display_startup_banner():
    """Display a beautiful startup banner"""
    console.clear()
    
    # Create title
    title = Text("🤖 INTELLIGENT CHATBOT", style="bold magenta", justify="center")
    
    # Create features table
    features_table = Table(show_header=False, box=None, padding=(0, 2))
    features_table.add_column("Icon", style="bold", width=4)
    features_table.add_column("Feature", style="cyan")
    
    features_table.add_row("🧮", "Mathematical calculations")
    features_table.add_row("🌤️", "Weather information")
    features_table.add_row("🖼️", "Image downloading from Google")
    
    # Create help text
    help_text = Text("Commands: Type 'quit', 'exit', or 'bye' to end the conversation", 
                    style="dim italic", justify="center")
    
    # Display everything in panels
    console.print(Panel(title, style="bold blue", padding=(1, 2)))
    console.print(Panel(features_table, title="✨ Available Tools", 
                       title_align="left", style="green", padding=(1, 2)))
    console.print(Panel(help_text, style="yellow", padding=(0, 2)))

def display_user_message(message):
    """Display user message with beautiful formatting"""
    user_text = Text(message, style="bold white")
    console.print(Panel(user_text, title="👤 You", title_align="left", 
                       style="blue", padding=(0, 1)))

def display_bot_response(response):
    """Display chatbot response with beautiful formatting"""
    # If response is a Table (weather), display it in a panel
    if hasattr(response, 'add_row'):
        console.print(Panel(response, title="🤖 Chatbot", title_align="left", 
                           style="green", padding=(1, 2)))
    else:
        # For text responses, check if it contains markdown-like formatting
        if any(marker in str(response) for marker in ['**', '*', '_', '`', '#']):
            # Render as markdown
            md_response = Markdown(str(response))
            console.print(Panel(md_response, title="🤖 Chatbot", title_align="left", 
                               style="green", padding=(1, 2)))
        else:
            # Regular text with rich formatting
            bot_text = Text(str(response))
            console.print(Panel(bot_text, title="🤖 Chatbot", title_align="left", 
                               style="green", padding=(1, 2)))

def get_user_input():
    """Get user input with a beautiful prompt"""
    console.print("\n💬", style="bold cyan", end=" ")
    return console.input("[bold cyan]Type your message:[/bold cyan] ")

def main():
    """Main function to run the chatbot"""
    
    # Display startup banner
    display_startup_banner()
    
    chatbot = IntelligentChatbot()
    
    while True:
        try:
            # Get user input
            user_input = get_user_input().strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                goodbye_text = Text("Goodbye! Have a great day! 👋", style="bold magenta", justify="center")
                console.print(Panel(goodbye_text, style="yellow", padding=(1, 2)))
                break
            
            if not user_input:
                continue
            
            # Display user message
            display_user_message(user_input)
            
            # Get and display bot response
            if chatbot.pending_action:
                response = chatbot.handle_pending_action(user_input)
            else:
                response = chatbot.chat(user_input)
            
            display_bot_response(response)
            
        except KeyboardInterrupt:
            console.print("\n")
            goodbye_text = Text("Goodbye! Have a great day! 👋", style="bold magenta", justify="center")
            console.print(Panel(goodbye_text, style="yellow", padding=(1, 2)))
            break
        except Exception as e:
            error_text = Text("Sorry, I encountered an error. Let's try again!", style="bold red")
            console.print(Panel(error_text, title="⚠️ Error", title_align="left", 
                               style="red", padding=(0, 1)))

if __name__ == "__main__":
    main()