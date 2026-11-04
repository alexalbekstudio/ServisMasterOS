from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ============================================
    # APP
    # ============================================
    APP_NAME: str = "ServisMasterOS"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # ============================================
    # DATABASE
    # ============================================
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "servismaster_db"

    # ============================================
    # JWT
    # ============================================
    SECRET_KEY: str = "promeni_ovaj_kljuc_u_produkciji_generisi_random_string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"

    # ============================================
    # CORS
    # ============================================
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://localhost:3000"

    # ============================================
    # PUBLIC URL (za notifikacije)
    # ============================================
    PUBLIC_BASE_URL: str = "http://localhost:8000"

    # ============================================
    # TELEGRAM (opciono)
    # ============================================
    TELEGRAM_BOT_TOKEN: str = "8693240161:AAGUExmbvItiRInZGpBHZZt3jsTx-7aCH6o"
    TELEGRAM_DEV_CHAT_ID: str = "7815212093"

    # ============================================
    # EMAIL (SMTP)
    # ============================================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "alexalbekstudio.design@gmail.com"
    SMTP_PASSWORD: str = "stcy zhsb nyhp ujzy"
    SMTP_FROM: str = "alexalbekstudio.design@gmail.com"
    TEST_EMAIL_RECIPIENT: str = "alexalbekstudio.design@gmail.com"
    SUPER_ADMIN_EMAIL: str = "alexalbekstudio.design@gmail.com"

    # ============================================
    # VIN DEKODER
    # ============================================
    NHTSA_API_URL: str = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin"

    # ============================================
    # FISKALIZACIJA (PFR)
    # ============================================
    PFR_SANDBOX_URL: str = "https://vsdc.sandbox.suf.purs.gov.rs"
    PFR_PRODUCTION_URL: str = "https://vsdc.suf.purs.gov.rs"
    PFR_CERTIFICATE_PATH: str = ""
    PFR_PAK_CODE: str = ""

    # ============================================
    # PROPERTY: DATABASE URL
    # ============================================
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ============================================
    # PYDANTIC SETTINGS CONFIG
    # ============================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        env_ignore_empty=True,
    )


settings = Settings()