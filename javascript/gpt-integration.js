import OpenAI from 'openai';
import dotenv from 'dotenv';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.resolve(__dirname, '..', '.env') });

export class GPTIntegration {
  constructor({ model = process.env.GPT_MODEL || 'gpt-5.5', apiKey = process.env.OPENAI_API_KEY } = {}) {
    if (!apiKey) {
      throw new Error('OPENAI_API_KEY is not configured');
    }

    this.client = new OpenAI({ apiKey });
    this.model = model;
    this.previousResponseId = null;
  }

  async chat(userMessage, systemPrompt = null) {
    if (typeof userMessage !== 'string' || !userMessage.trim()) {
      throw new TypeError('userMessage must be a non-empty string');
    }
    if (systemPrompt !== null && (typeof systemPrompt !== 'string' || !systemPrompt.trim())) {
      throw new TypeError('systemPrompt must be a non-empty string or null');
    }

    const request = {
      model: this.model,
      input: userMessage,
    };

    if (systemPrompt) {
      request.instructions = systemPrompt;
    }
    if (this.previousResponseId) {
      request.previous_response_id = this.previousResponseId;
    }

    const response = await this.client.responses.create(request);
    const assistantMessage = response.output_text?.trim();

    if (!assistantMessage) {
      throw new Error(`OpenAI returned an empty response${response.id ? ` (${response.id})` : ''}`);
    }

    this.previousResponseId = response.id;
    return assistantMessage;
  }

  resetConversation() {
    this.previousResponseId = null;
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
    if (style !== null && (typeof style !== 'string' || !style.trim())) {
      throw new TypeError('style must be a non-empty string or null');
    }

    const prompt = style
      ? `Generate content about: ${topic} in a ${style} style.`
      : `Generate content about: ${topic}`;
    return this.chat(prompt);
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  const gpt = new GPTIntegration();
  const response = await gpt.chat('Hello! How are you?');
  console.log(`Assistant: ${response}`);
}
