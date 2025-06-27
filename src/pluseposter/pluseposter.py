from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
from .config import Config
from .utils import logger
from .platforms.base import Platform


class PlusePoster:
    """
    🚀 Main PlusePoster class that handles all social media operations
    
    This class is your friendly interface to all social media platforms.
    It manages platform connections, posts content, and handles scheduling.
    
    Usage:
    ```python
    # Create a new PlusePoster instance
    poster = PlusePoster()
    
    # Post content
    await poster.post(
        platform="twitter",
        content_type="text",
        content="Hello world!"
    )
    ```
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        📌 Initialize PlusePoster with configuration
        
        Args:
            config (Optional[Dict[str, Any]]): Configuration dictionary
                - If None, loads from environment variables
                - Supports Twitter, Instagram, and Facebook
        """
        self.config = Config(config)
        self.logger = logger
        self.platforms: Dict[str, Platform] = {}
        self._initialize_platforms()

    def _initialize_platforms(self):
        """
        🔄 Set up all supported social media platforms
        
        This method automatically connects to all configured platforms:
        - Twitter (if TWITTER_API_KEY is set)
        - Instagram (if INSTAGRAM_API_KEY is set)
        - Facebook (if FACEBOOK_API_KEY is set)
        
        Each platform is initialized with its own configuration.
        """
        from .platforms.twitter import TwitterPlatform
        from .platforms.instagram import InstagramPlatform
        from .platforms.facebook import FacebookPlatform
        
        # Initialize platforms if configured
        if self.config.twitter:
            self.platforms["twitter"] = TwitterPlatform(self.config.twitter)
        if self.config.instagram:
            self.platforms["instagram"] = InstagramPlatform(self.config.instagram)
        if self.config.facebook:
            self.platforms["facebook"] = FacebookPlatform(self.config.facebook)

    async def post(
        self,
        platform: str,
        content_type: str,
        content: Any,
        caption: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        📱 Post content to a social media platform
        
        Args:
            platform (str): Platform name (twitter, instagram, facebook)
            content_type (str): Type of content (text, image, video)
            content (Any): Content to post
                - For text: just the text message
                - For media: path to file
            caption (Optional[str]): Caption for media posts
            scheduled_time (Optional[datetime]): Time to schedule the post
                - If None, posts immediately
                - Format: YYYY-MM-DDTHH:MM:SS
                
        Returns:
            Dict[str, Any]: Response from the platform
            
        Example:
        ```python
        # Post text
        await poster.post(
            platform="twitter",
            content_type="text",
            content="Hello world!"
        )
        
        # Post image with caption
        await poster.post(
            platform="instagram",
            content_type="image",
            content="path/to/image.jpg",
            caption="Check out this image!"
        )
        ```
        """
        if platform not in self.platforms:
            raise ValueError(f"Platform '{platform}' is not supported")

        platform_instance = self.platforms[platform]
        return await platform_instance.post(
            content_type=content_type,
            content=content,
            caption=caption,
            scheduled_time=scheduled_time,
        )

    async def schedule_post(
        self,
        platform: str,
        content_type: str,
        content: Any,
        caption: Optional[str] = None,
        scheduled_time: datetime,
    ) -> Dict[str, Any]:
        """
        📅 Schedule a post for a future time
        
        This method is a convenience wrapper around the post() method
        that automatically sets the scheduled_time parameter.
        
        Args:
            platform (str): Platform name
            content_type (str): Type of content
            content (Any): Content to post
            caption (Optional[str]): Caption for the post
            scheduled_time (datetime): Time to schedule the post
                - Must be in the future
                - Format: YYYY-MM-DDTHH:MM:SS
                
        Returns:
            Dict[str, Any]: Scheduling response
            
        Example:
        ```python
        # Schedule a post for tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        await poster.schedule_post(
            platform="facebook",
            content_type="text",
            content="Good morning!",
            scheduled_time=tomorrow
        )
        ```
        """
        return await self.post(
            platform=platform,
            content_type=content_type,
            content=content,
            caption=caption,
            scheduled_time=scheduled_time,
        )

    async def close(self):
        """
        🔒 Clean up all platform connections
        
        This method should be called when you're done using PlusePoster.
        It ensures all platform sessions are properly closed.
        
        Example:
        ```python
        # Close all connections
        await poster.close()
        ```
        """
        for platform in self.platforms.values():
            await platform.close()

    def _initialize_platforms(self):
        """Initialize all supported platforms"""
        from .platforms.twitter import TwitterPlatform
        from .platforms.instagram import InstagramPlatform
        from .platforms.facebook import FacebookPlatform
        
        # Initialize platforms if configured
        if self.config.twitter:
            self.platforms["twitter"] = TwitterPlatform(self.config.twitter)
        if self.config.instagram:
            self.platforms["instagram"] = InstagramPlatform(self.config.instagram)
        if self.config.facebook:
            self.platforms["facebook"] = FacebookPlatform(self.config.facebook)

    async def post(
        self,
        platform: str,
        content_type: str,
        content: Any,
        caption: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Post content to a specific platform
        
        Args:
            platform (str): Platform name (twitter, instagram, etc.)
            content_type (str): Type of content (text, image, video)
            content (Any): Content to post
            caption (Optional[str]): Caption for the post
            scheduled_time (Optional[datetime]): Time to schedule the post
            
        Returns:
            Dict[str, Any]: Response from the platform
        """
        if platform not in self.platforms:
            raise ValueError(f"Platform '{platform}' is not supported")

        platform_instance = self.platforms[platform]
        return await platform_instance.post(
            content_type=content_type,
            content=content,
            caption=caption,
            scheduled_time=scheduled_time,
        )

    async def schedule_post(
        self,
        platform: str,
        content_type: str,
        content: Any,
        caption: Optional[str] = None,
        scheduled_time: datetime,
    ) -> Dict[str, Any]:
        """
        Schedule a post for a future time
        
        Args:
            platform (str): Platform name
            content_type (str): Type of content
            content (Any): Content to post
            caption (Optional[str]): Caption for the post
            scheduled_time (datetime): Time to schedule the post
            
        Returns:
            Dict[str, Any]: Scheduling response
        """
        return await self.post(
            platform=platform,
            content_type=content_type,
            content=content,
            caption=caption,
            scheduled_time=scheduled_time,
        )

    async def close(self):
        """
        🔒 Clean up all platform connections
        
        This method should be called when you're done using PlusePoster.
        It ensures all platform sessions are properly closed.
        
        Example:
        ```python
        # Close all connections
        await poster.close()
        ```
        """
        for platform in self.platforms.values():
            await platform.close()
