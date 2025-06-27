import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

class PlatformConfig(BaseModel):
    api_key: str
    api_secret: str
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None

class Config(BaseModel):
    twitter: Optional[PlatformConfig] = None
    instagram: Optional[PlatformConfig] = None
    facebook: Optional[PlatformConfig] = None

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        load_dotenv()
        return cls(
            twitter=PlatformConfig(
                api_key=os.getenv("TWITTER_API_KEY"),
                api_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
            ) if os.getenv("TWITTER_API_KEY") else None,
            instagram=PlatformConfig(
                api_key=os.getenv("INSTAGRAM_API_KEY"),
                api_secret=os.getenv("INSTAGRAM_API_SECRET"),
            ) if os.getenv("INSTAGRAM_API_KEY") else None,
            facebook=PlatformConfig(
                api_key=os.getenv("FACEBOOK_API_KEY"),
                api_secret=os.getenv("FACEBOOK_API_SECRET"),
            ) if os.getenv("FACEBOOK_API_KEY") else None,
        )

    @classmethod
    def from_yaml(cls, path: Path) -> "Config":
        """Load configuration from YAML file"""
        with open(path, "r") as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return self.dict(exclude_none=True)
