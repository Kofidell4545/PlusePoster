from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
import json
from time import sleep
import aiohttp
from PIL import Image
from .base import Platform
from instagrapi import Client


class InstagramPlatform(Platform):
    """
    Instagram platform implementation using instagrapi
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger("pluseposter.instagram")
        self.client = None
        self._ensure_client()

    def _ensure_client(self):
        """Initialize or get Instagram client"""
        if not self.client:
            self.client = Client()
            try:
                self.client.login(
                    self.config.api_key,  # username
                    self.config.api_secret,  # password
                )
            except Exception as e:
                self.logger.error(f"Instagram login failed: {str(e)}")
                raise

    async def _validate_image(self, file_path: str) -> bool:
        """
        Validate Instagram image requirements
        
        Args:
            file_path (str): Path to image file
            
        Returns:
            bool: True if image is valid
        """
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                # Instagram requirements
                if width < 320 or height < 320:
                    return False
                if width > 1080 or height > 1080:
                    return False
                if img.format not in ['JPEG', 'PNG']:
                    return False
            return True
        except Exception:
            return False

    async def _validate_video(self, file_path: str) -> bool:
        """
        Validate Instagram video requirements
        
        Args:
            file_path (str): Path to video file
            
        Returns:
            bool: True if video is valid
        """
        try:
            # TODO: Implement video validation using moviepy or similar
            return True
        except Exception:
            return False

    async def post(
        self,
        content_type: str,
        content: Any,
        caption: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Post content to Instagram
        
        Args:
            content_type (str): Type of content (image, video)
            content (Any): Content to post
            caption (Optional[str]): Caption for the post
            scheduled_time (Optional[datetime]): Time to schedule the post
            
        Returns:
            Dict[str, Any]: Response from Instagram API
        """
        if not self._validate_content(content_type, content):
            raise ValueError("Invalid content")

        file_path = validate_file_path(content)
        
        # Handle scheduling
        await self._handle_scheduling(scheduled_time)

        try:
            if content_type == "image":
                if not await self._validate_image(file_path):
                    raise ValueError("Image does not meet Instagram requirements")
                
                result = self.client.photo_upload(
                    file_path,
                    caption=caption or ""
                )

            elif content_type == "video":
                if not await self._validate_video(file_path):
                    raise ValueError("Video does not meet Instagram requirements")
                
                result = self.client.video_upload(
                    file_path,
                    caption=caption or ""
                )

            else:
                raise ValueError(f"Unsupported content type: {content_type}")

            return {
                "success": True,
                "post_id": result.id,
                "media_type": result.media_type,
                "caption": caption,
            }

        except Exception as e:
            self.logger.error(f"Instagram post failed: {str(e)}")
            raise

    async def close(self):
        """Close Instagram session"""
        if self.client:
            self.client.logout()
            self.client = None
