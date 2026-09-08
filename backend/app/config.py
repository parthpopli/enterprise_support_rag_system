from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "Enterprise Support RAG"

    debug: bool = True

    groq_api_key: str

    llm_model: str = "openai/gpt-oss-120b"

    embedding_model: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()