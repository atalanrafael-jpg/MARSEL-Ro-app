import OpenAI from 'openai';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: '../.env' });

// Initialize OpenAI client
const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

class GPTIntegration {
  constructor(model = null) {
    this.model = model || process.env.GPT_MODEL || 'gpt-3.5-turbo';
    this.conversationHistory = [];
  }

  async chat(userMessage, systemPrompt = null) {
    const messages = [];

    if (systemPrompt) {
      messages.push({ role: 'system', content: systemPrompt });
    }

    // Add conversation history
    messages.push(...this.conversationHistory);

    // Add current message
    messages.push({ role: 'user', content: userMessage });

    try {
      const response = await client.chat.completions.create({
        model: this.model,
        messages: messages,
        temperature: 0.7,
        max_tokens: 2000,
      });

      const assistantMessage = response.choices[0].message.content;

      // Store in conversation history
      this.conversationHistory.push({ role: 'user', content: userMessage });
      this.conversationHistory.push({ role: 'assistant', content: assistantMessage });

      return assistantMessage;
    } catch (error) {
      return `Error: ${error.message}`;
    }
  }

  resetConversation() {
    this.conversationHistory = [];
  }

  async analyzeText(text) {
    const prompt = `Please analyze the following text:\n\n${text}`;
    return this.chat(prompt);
  }

  async generateContent(topic, style = null) {
    let prompt = `Generate content about: ${topic}`;
    if (style) {
      prompt += ` in a ${style} style.`;
    }
    return this.chat(prompt);
  }
}

// Example usage
async function main() {
  const gpt = new GPTIntegration();

  // Example 1: Simple chat
  console.log('Example 1: Simple Chat');
  const response1 = await gpt.chat('Hello! How are you?');
  console.log(`Assistant: ${response1}\n`);

  // Example 2: Continue conversation
  console.log('Example 2: Continue Conversation');
  const response2 = await gpt.chat('Can you tell me more about JavaScript?');
  console.log(`Assistant: ${response2}\n`);

  // Example 3: Analyze text
  console.log('Example 3: Analyze Text');
  gpt.resetConversation();
  const analysis = await gpt.analyzeText('Artificial Intelligence is transforming the world.');
  console.log(`Analysis: ${analysis}\n`);

  // Example 4: Generate content
  console.log('Example 4: Generate Content');
  const content = await gpt.generateContent('Web Development basics', 'educational');
  console.log(`Generated Content: ${content}`);
}

main().catch(console.error);
