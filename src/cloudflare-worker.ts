import { Container, getContainer } from "@cloudflare/containers";
import { env } from "cloudflare:workers";

export class MarselRoAppContainer extends Container {
  defaultPort = 8000;
  sleepAfter = "10m";
  envVars = {
    ROAPP_BASE_URL: env.ROAPP_BASE_URL,
    ROAPP_API_KEY: env.ROAPP_API_KEY,
    ROAPP_TIMEOUT_SECONDS: env.ROAPP_TIMEOUT_SECONDS,
    ROAPP_MAX_REQUESTS_PER_SECOND: env.ROAPP_MAX_REQUESTS_PER_SECOND,
    ROAPP_MAX_RETRIES: env.ROAPP_MAX_RETRIES,
    ROAPP_RETRY_BASE_SECONDS: env.ROAPP_RETRY_BASE_SECONDS,
    OPENAI_ADS_PIXEL_ID: env.OPENAI_ADS_PIXEL_ID,
    OPENAI_ADS_CONVERSIONS_API_KEY: env.OPENAI_ADS_CONVERSIONS_API_KEY,
    OPENAI_ADS_BASE_URL: env.OPENAI_ADS_BASE_URL,
    OPENAI_ADS_VALIDATE_ONLY: env.OPENAI_ADS_VALIDATE_ONLY,
    OPENAI_ADS_DEFAULT_CURRENCY: env.OPENAI_ADS_DEFAULT_CURRENCY,
    OPENAI_ADS_SOURCE_URL: env.OPENAI_ADS_SOURCE_URL ?? "",
    OPENAI_ADS_TIMEOUT_SECONDS: env.OPENAI_ADS_TIMEOUT_SECONDS,
  };
}

export default {
  async fetch(request: Request, _env: unknown, _ctx: ExecutionContext) {
    const container = getContainer(env.MARSEL_ROAPP_CONTAINER, "production");
    return container.fetch(request);
  },
};
