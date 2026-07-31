import OpenAI from 'openai';
import * as dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: '../.env' });

// Initialize OpenAI client
const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

class GPTIntegration {
  private model: string;
  private conversationHistory: Message[] = [];

  constructor(model?: string) {
    this.model = model || process.env.GPT_MODEL || 'gpt-3.5-turbo';
  }

  async chat(userMessage: string, systemPrompt?: string): Promise<string> {
    const messages: Message[] = [];

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

      const assistantMessage = response.choices[0].message.content || '';

      // Store in conversation history
      this.conversationHistory.push({ role: 'user', content: userMessage });
      this.conversationHistory.push({ role: 'assistant', content: assistantMessage });

      return assistantMessage;
    } catch (error) {
      if (error instanceof Error) {
        return `Error: ${error.message}`;
      }
      return 'An unknown error occurred';
    }
  }

  resetConversation(): void {
    this.conversationHistory = [];
  }

  async analyzeText(text: string): Promise<string> {
    const prompt = `Please analyze the following text:\n\n${text}`;
    return this.chat(prompt);
  }

  async generateContent(topic: string, style?: string): Promise<string> {
    let prompt = `Generate content about: ${topic}`;
    if (style) {
      prompt += ` in a ${style} style.`;
    }
    return this.chat(prompt);
  }
}

// Example usage
async function main(): Promise<void> {
  const gpt = new GPTIntegration();

  // Example 1: Simple chat
  console.log('Example 1: Simple Chat');
  const response1 = await gpt.chat('Hello! How are you?');
  console.log(`Assistant: ${response1}\n`);

  // Example 2: Continue conversation
  console.log('Example 2: Continue Conversation');
  const response2 = await gpt.chat('Can you tell me more about TypeScript?');
  console.log(`Assistant: ${response2}\n`);

  // Example 3: Analyze text
  console.log('Example 3: Analyze Text');
  gpt.resetConversation();
  const analysis = await gpt.analyzeText('Artificial Intelligence is transforming the world.');
  console.log(`Analysis: ${analysis}\n`);

  // Example 4: Generate content
  console.log('Example 4: Generate Content');
  const content = await gpt.generateContent('API Development', 'technical');
  console.log(`Generated Content: ${content}`);
}

main().catch(console.error);
