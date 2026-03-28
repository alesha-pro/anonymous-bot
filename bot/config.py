from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    telegram_bot_token: str = ""

    # OpenRouter / LLM
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "google/gemini-2.5-flash-preview"

    # Embeddings (may differ from OpenRouter if it lacks /v1/embeddings)
    embed_base_url: str | None = None
    openrouter_embed_model: str = "text-embedding-3-small"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "na_documents"

    # Agent
    history_max_messages: int = 20

    @property
    def effective_embed_base_url(self) -> str:
        return self.embed_base_url or self.openrouter_base_url
