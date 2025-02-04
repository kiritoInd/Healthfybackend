from pydantic_settings import BaseSettings
from urllib.parse import quote_plus

class Settings(BaseSettings):
    # Project metadata
    PROJECT_NAME: str = "HBackend"
    VERSION: str = "1.0.0"

    # MongoDB Credentials
    MONGO_USERNAME: str
    MONGO_PASSWORD: str
    MONGO_CLUSTER: str
    MONGO_DBNAME: str

    # API Keys
    OPENAI_API_KEY: str
    GROQ_API_KEY: str
    PUBMED_API_BASE: str

    # JWT Authentication
    JWT_SECRET: str
    ALGORITHM: str
    @property
    def MONGO_URI(self) -> str:
        """
        Construct the MongoDB URI with escaped username and password.
        """
        username = quote_plus(self.MONGO_USERNAME)
        password = quote_plus(self.MONGO_PASSWORD)
        return f"mongodb+srv://{username}:{password}@{self.MONGO_CLUSTER}/{self.MONGO_DBNAME}?retryWrites=true&w=majority"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in the .env file

# Create an instance of Settings
settings = Settings()