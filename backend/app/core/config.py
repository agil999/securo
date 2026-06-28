from functools import lru_cache
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_name: str = "Securo"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/securo"

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not value:
            return value

        parsed = urlparse(value)

        scheme = parsed.scheme
        if scheme in {"postgres", "postgresql"}:
            scheme = "postgresql+asyncpg"

        query = dict(parse_qsl(parsed.query, keep_blank_values=True))

        if query.pop("sslmode", None) == "require":
            query["ssl"] = "require"

        hostname = parsed.hostname or ""
        if "supabase" in hostname and "prepared_statement_cache_size" not in query:
            query["prepared_statement_cache_size"] = "0"

        return urlunparse(parsed._replace(scheme=scheme, query=urlencode(query)))

    # Auth
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Pluggy
    pluggy_client_id: str = ""
    pluggy_client_secret: str = ""
    pluggy_oauth_redirect_uri: str = "http://localhost:5173/oauth/callback"

    # Enable Banking
    enable_banking_app_id: str = ""
    enable_banking_private_key: str = ""
    enable_banking_private_key_file: str = ""
    enable_banking_api_url: str = "https://api.enablebanking.com"
    enable_banking_oauth_redirect_uri: str = "http://localhost:5173/oauth/callback"

    # SimpleFIN
    simplefin_enabled: bool = False
    simplefin_api_url: str = "https://beta-bridge.simplefin.org"

    # Frontend
    frontend_url: str = "http://localhost:5173"

    # WebAuthn / passkeys
    webauthn_rp_name: str = "Securo"
    webauthn_rp_id: str = ""
    webauthn_origin: str = ""
    webauthn_challenge_ttl_seconds: int = 300

    @property
    def resolved_webauthn_origin(self) -> str:
        return self.webauthn_origin or self.frontend_url

    @property
    def resolved_webauthn_rp_id(self) -> str:
        if self.webauthn_rp_id:
            return self.webauthn_rp_id

        parsed = urlparse(self.frontend_url)
        return parsed.hostname or "localhost"

    # Defaults
    default_currency: str = "USD"

    # FX Rates
    openexchangerates_app_id: str = ""
    supported_currencies: str = (
        "USD,EUR,GBP,BRL,CAD,AUD,CHF,ARS,JPY,MXN,INR,"
        "SEK,DKK,NOK,PLN,CZK,HUF,RON,CRC,IDR,COP,CLP,DOP,RUB"
    )
    fx_sync_mode: str = "on_demand"

    # Storage
    storage_provider: str = "local"
    storage_local_path: str = "./data/attachments"
    storage_max_file_size_mb: int = 10
    storage_allowed_extensions: str = "jpg,jpeg,png,webp,gif,heic,pdf"
    storage_max_attachments_per_transaction: int = 10

    # S3 Storage
    storage_s3_bucket: str = ""
    storage_s3_region: str = ""
    storage_s3_access_key: str = ""
    storage_s3_secret_key: str = ""
    storage_s3_endpoint_url: str = ""

    # Registration
    registration_enabled: bool = True

    # OIDC login
    oidc_enabled: bool = False
    oidc_provider_name: str = "OIDC"
    oidc_discovery_url: str = ""
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_redirect_uri: str = ""
    oidc_scopes: str = "openid email profile"
    oidc_auto_register: bool = True
    oidc_existing_user_link_mode: str = "disabled"
    oidc_require_verified_email: bool = True
    oidc_sync_roles: bool = False
    oidc_roles_claim: str = "groups"
    oidc_admin_roles: str = ""
    oidc_workspace_role_map: str = ""

    # Celery / Redis
    redis_url: str = "redis://localhost:6379/0"

    # Logo
    logo_size: int = 128

    # Brazilian Treasury bond prices
    tesouro_direto_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
