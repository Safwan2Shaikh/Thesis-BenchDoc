import os


class Settings:
    use_legacy_layout: bool = os.getenv("THESIS_USE_LEGACY_LAYOUT", "0") == "1"


settings = Settings()
