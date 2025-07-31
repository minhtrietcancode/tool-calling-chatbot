import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Import the packages of 3 tools we have just created 
import src.tools.check_weather.weather_checking as check_weather
from src.tools.image_crawler.ImageCrawler import AutoCrawler
import src.tools.my_calculator.calculator as calculator 

# Load the API key getting from openrouter
load_dotenv()
openai_api_key = os.getenv("OPENROUTER_API_KEY")

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
            print(f"Error in analysis: {e}")
            return {"action": "chat", "response": "Sorry, I had trouble understanding that. Could you try again?"}
    
    def execute_tool(self, tool, params):
        """Execute the specified tool with given parameters"""
        
        try:
            if tool == "calculator":
                result = calculator.calculator_tool(params["expression"])
                if result["error"]:
                    return f"Sorry, I couldn't calculate that: {result['error']}"
                else:
                    return f"The answer is: {result['result']}"
            
            elif tool == "weather":
                result = check_weather.get_weather_info(params["location"])
                if "error" in result:
                    return f"Sorry, I couldn't get weather info: {result['error']}"
                else:
                    return (f"Weather in {result['location']}, {result['country']}:\n"
                           f"🌡️ Temperature: {result['temperature']}°C (feels like {result['feels_like']}°C)\n"
                           f"☁️ Conditions: {result['description']}\n"
                           f"💧 Humidity: {result['humidity']}%\n"
                           f"🌬️ Wind: {result['wind_speed']} km/h\n"
                           f"👁️ Visibility: {result['visibility']} km")
            
            elif tool == "images":
                keyword = params["keyword"]
                count = params.get("count", 5)
                
                success = self.image_crawler.download_keyword_images(keyword, count)
                if success:
                    return f"Successfully downloaded {count} images of '{keyword}'! Check the 'downloaded_images/{keyword}/' folder."
                else:
                    return f"Sorry, I couldn't download images of '{keyword}' right now."
        
        except Exception as e:
            return f"Sorry, I'm currently unavailable for this request."
    
    def generate_response(self, user_message, tool_result=None):
        """Step 2: Generate natural response, optionally including tool results"""
        
        context = f"User said: {user_message}"
        if tool_result:
            context += f"\nTool result: {tool_result}"
            system_prompt = "You are a friendly chatbot. The user asked something and you used a tool to help them. Respond naturally and conversationally, incorporating the tool result into your response."
        else:
            system_prompt = "You are a friendly chatbot. Respond naturally and conversationally to the user's message."
        
        try:
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
            response = self.generate_response(user_message, tool_result)
            
        elif analysis["action"] == "suggest_tool":
            # Suggest using a tool
            response = analysis["suggestion"]
            self.pending_action = {"tool": analysis["tool"], "keyword": self.extract_keyword_from_message(user_message)}
            
        elif analysis["action"] == "ask_clarification":
            # Ask for missing information
            response = analysis["question"]
            self.pending_action = {"tool": analysis["tool"], "waiting_for": "clarification"}
            
        else:
            # Normal chat
            response = analysis["response"]
        
        # Add response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
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
                return self.generate_response(f"weather in {user_response}", tool_result)
            
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

def main():
    """Main function to run the chatbot"""
    
    print("🤖 Intelligent Chatbot Started!")
    print("I can help you with calculations, weather info, and downloading images!")
    print("Type 'quit' to exit.\n")
    
    chatbot = IntelligentChatbot()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("Chatbot: Goodbye! Have a great day! 👋")
                break
            
            if not user_input:
                continue
            
            # Check if we have a pending action
            if chatbot.pending_action:
                response = chatbot.handle_pending_action(user_input)
            else:
                response = chatbot.chat(user_input)
            
            print(f"Chatbot: {response}\n")
            
        except KeyboardInterrupt:
            print("\nChatbot: Goodbye! Have a great day! 👋")
            break
        except Exception as e:
            print(f"Chatbot: Sorry, I encountered an error. Let's try again!")

if __name__ == "__main__":
    main()