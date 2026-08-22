import OpenAI from 'openai';
import * as dotenv from 'dotenv';

// Resolve .env from the repository root when this module is executed from any cwd.
dotenv.config();

interface GPTClient {
  responses: {
    create: (request: Record<string, unknown>) => Promise<{
      id: string;
      output_text?: string;
    }>;
  };
}

export class GPTIntegration {
  private readonly client: GPTClient;
  private readonly model: string;
  private previousResponseId?: string;

  constructor(model?: string, client?: GPTClient) {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!client && !apiKey) {
      throw new Error('OPENAI_API_KEY is required');
    }

    this.client = client ?? new OpenAI({ apiKey }) as unknown as GPTClient;
    this.model = model || process.env.GPT_MODEL || 'gpt-5.5';
  }

  async chat(userMessage: string, systemPrompt?: string): Promise<string> {
    if (!userMessage.trim()) {
      throw new Error('userMessage must be a non-empty string');
    }

    const request: Record<string, unknown> = {
      model: this.model,
      input: userMessage.trim(),
      store: true,
    };

    if (systemPrompt?.trim()) {
      request.instructions = systemPrompt.trim();
    }
    if (this.previousResponseId) {
      request.previous_response_id = this.previousResponseId;
    }

    const response = await this.client.responses.create(request);
    this.previousResponseId = response.id;
    const text = response.output_text?.trim() ?? '';
    if (!text) {
      throw new Error('OpenAI returned an empty response');
    }
    return text;
  }

  resetConversation(): void {
    this.previousResponseId = undefined;
  }

  analyzeText(text: string): Promise<string> {
    if (!text.trim()) {
      throw new Error('text must be a non-empty string');
    }
    return this.chat(`Please analyze the following text:\n\n${text.trim()}`);
  }

  generateContent(topic: string, style?: string): Promise<string> {
    if (!topic.trim()) {
      throw new Error('topic must be a non-empty string');
    }
    let prompt = `Generate content about: ${topic.trim()}`;
    if (style?.trim()) {
      prompt += ` in a ${style.trim()} style.`;
    }
    return this.chat(prompt);
  }
}

if (process.argv[1]?.endsWith('gpt-integration.ts')) {
  const gpt = new GPTIntegration();
  gpt.chat('Hello! How are you?').then(console.log).catch((error: unknown) => {
    console.error(error);
    process.exitCode = 1;
  });
}
