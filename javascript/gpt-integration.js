import OpenAI from 'openai';
import dotenv from 'dotenv';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.resolve(__dirname, '..', '.env') });

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export class GPTIntegration {
  constructor(model = process.env.GPT_MODEL || 'gpt-5.6-luna') {
    if (!process.env.OPENAI_API_KEY) {
      throw new Error('OPENAI_API_KEY is not configured');
    }
    this.model = model;
    this.conversationHistory = [];
  }

  async chat(userMessage, systemPrompt = null) {
    if (typeof userMessage !== 'string' || !userMessage.trim()) {
      throw new TypeError('userMessage must be a non-empty string');
    }

    const input = [];
    if (systemPrompt) {
      input.push({ role: 'system', content: systemPrompt });
    }
    input.push(...this.conversationHistory);
    input.push({ role: 'user', content: userMessage });

    const response = await client.responses.create({
      model: this.model,
      input,
    });

    const assistantMessage = response.output_text?.trim();
    if (!assistantMessage) {
      throw new Error('OpenAI returned an empty response');
    }

    this.conversationHistory.push({ role: 'user', content: userMessage });
    this.conversationHistory.push({ role: 'assistant', content: assistantMessage });

    return assistantMessage;
  }

  resetConversation() {
    this.conversationHistory = [];
  }

  async analyzeText(text) {
    if (typeof text !== 'string' || !text.trim()) {
      throw new TypeError('text must be a non-empty string');
    }
    return this.chat(`Please analyze the following text:\n\n${text}`);
  }

  async generateContent(topic, style = null) {
    if (typeof topic !== 'string' || !topic.trim()) {
      throw new TypeError('topic must be a non-empty string');
    }
    const prompt = style
      ? `Generate content about: ${topic} in a ${style} style.`
      : `Generate content about: ${topic}`;
    return this.chat(prompt);
  }
}

// Run the examples only when this file is executed directly.
if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const gpt = new GPTIntegration();
  const response = await gpt.chat('Hello! How are you?');
  console.log(`Assistant: ${response}`);
}
