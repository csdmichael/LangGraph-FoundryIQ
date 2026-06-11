"""Centralized settings for the LangGraph-FoundryIQ API."""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Azure / Foundry ---
    azure_subscription_id: str = Field(default="")
    azure_resource_group: str = Field(default="")
    azure_tenant_id: str = Field(default="")

    foundry_project_name: str = Field(default="proj-default")
    foundry_account_name: str = Field(default="002-ai-poc-private")
    foundry_agent_id: str = Field(default="sp-search")

    # --- APIM AI Gateway (mandatory — only path to Foundry) ---
    apim_base_url: str = Field(default="")
    apim_foundry_path: str = Field(default="/foundry/agents")
    apim_subscription_key: str = Field(default="")

    # --- Azure AI Search ---
    azure_search_endpoint: str = Field(default="")
    azure_search_index_name: str = Field(default="sp-search-index")
    azure_search_api_key: str = Field(default="")

    # --- App ---
    log_level: str = Field(default="INFO")
    cors_origins: str = Field(default="http://localhost:8100,http://localhost:4200")

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def foundry_gateway_url(self) -> str:
        """Resolve the Foundry agent URL via APIM. APIM is required."""
        if not self.apim_base_url:
            raise RuntimeError(
                "APIM_BASE_URL is not configured. All Foundry traffic must flow "
                "through the APIM AI Gateway — direct Foundry access is disabled."
            )
        base = self.apim_base_url.rstrip("/")
        path = self.apim_foundry_path.strip("/")
        return f"{base}/{path}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
