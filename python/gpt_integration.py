import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class GPTIntegration:
    def __init__(self, model: str = None):
        """Initialize GPT Integration
        
        Args:
            model: Model name (gpt-4 or gpt-3.5-turbo). Defaults to env variable.
        """
        self.model = model or os.getenv('GPT_MODEL', 'gpt-3.5-turbo')
        self.conversation_history = []
    
    def chat(self, user_message: str, system_prompt: str = None) -> str:
        """Send a message to GPT and get a response
        
        Args:
            user_message: User message
            system_prompt: Optional system prompt for context
            
        Returns:
            Assistant response
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            assistant_message = response.choices[0].message.content
            
            # Store in conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
        except Exception as e:
            return f"Error: {str(e)}"
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def analyze_text(self, text: str) -> str:
        """Analyze text using GPT
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis result
        """
        prompt = f"Please analyze the following text:\n\n{text}"
        return self.chat(prompt)
    
    def generate_content(self, topic: str, style: str = None) -> str:
        """Generate content based on topic
        
        Args:
            topic: Topic for content generation
            style: Optional style/tone specification
            
        Returns:
            Generated content
        """
        prompt = f"Generate content about: {topic}"
        if style:
            prompt += f" in a {style} style."
        return self.chat(prompt)

# Example usage
if __name__ == "__main__":
    # Initialize GPT
    gpt = GPTIntegration()
    
    # Example 1: Simple chat
    response = gpt.chat("Hello! How are you?")
    print(f"Assistant: {response}\n")
    
    # Example 2: Continue conversation
    response = gpt.chat("Can you tell me more about Python?")
    print(f"Assistant: {response}\n")
    
    # Example 3: Analyze text
    gpt.reset_conversation()
    analysis = gpt.analyze_text("Artificial Intelligence is transforming the world.")
    print(f"Analysis: {analysis}\n")
    
    # Example 4: Generate content
    content = gpt.generate_content("Machine Learning basics", "educational")
    print(f"Generated Content: {content}")
