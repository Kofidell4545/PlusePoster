from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
import logging
from .base import Platform
from ..utils import validate_file_path


class TwitterPlatform(Platform):
    """
    Twitter platform implementation
    """
    API_URL = "https://api.twitter.com/2"
    MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger("pluseposter.twitter")
        self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create a new aiohttp session"""
        if not self.session:
            auth = aiohttp.BasicAuth(
                self.config.api_key,
                self.config.api_secret
            )
            self.session = aiohttp.ClientSession(auth=auth)
        return self.session

    async def _upload_media(self, file_path: str) -> str:
        """
        Upload media to Twitter
        
        Args:
            file_path (str): Path to the media file
            
        Returns:
            str: Media ID from Twitter
        """
        session = await self._get_session()
        
        # Step 1: Initialize upload
        async with session.post(
            self.MEDIA_UPLOAD_URL,
            params={"command": "INIT", "media_type": "image/jpeg"},
        ) as resp:
            init_data = await resp.json()
            media_id = init_data["media_id_string"]

        # Step 2: Upload chunks
        file_path = validate_file_path(file_path)
        with open(file_path, "rb") as f:
            chunk = f.read(4 * 1024 * 1024)  # 4MB chunks
            while chunk:
                async with session.post(
                    self.MEDIA_UPLOAD_URL,
                    params={
                        "command": "APPEND",
                        "media_id": media_id,
                        "segment_index": 0,
                    },
                    data=chunk,
                ) as resp:
                    if resp.status != 204:
                        raise Exception("Failed to upload media chunk")
                chunk = f.read(4 * 1024 * 1024)

        # Step 3: Finalize upload
        async with session.post(
            self.MEDIA_UPLOAD_URL,
            params={"command": "FINALIZE", "media_id": media_id},
        ) as resp:
            finalize_data = await resp.json()
            if finalize_data.get("processing_info"):
                # TODO: Handle processing
                pass

        return media_id

    async def post(
        self,
        content_type: str,
        content: Any,
        caption: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Post content to Twitter
        
        Args:
            content_type (str): Type of content (text, image, video)
            content (Any): Content to post
            caption (Optional[str]): Caption for the post
            scheduled_time (Optional[datetime]): Time to schedule the post
            
        Returns:
            Dict[str, Any]: Response from Twitter API
        """
        if not self._validate_content(content_type, content):
            raise ValueError("Invalid content")

        session = await self._get_session()
        
        # Handle different content types
        if content_type == "text":
            text = content if isinstance(content, str) else caption
            if not text:
                raise ValueError("Text content is required")
            
            payload = {
                "text": text[:280],  # Twitter's character limit
            }

        elif content_type in ["image", "video"]:
            if not isinstance(content, str):
                raise ValueError("File path is required for media content")
            
            media_id = await self._upload_media(content)
            payload = {
                "text": caption[:280] if caption else "",
                "media": {
                    "media_ids": [media_id],
                },
            }

        else:
            raise ValueError(f"Unsupported content type: {content_type}")

        # Handle scheduling
        await self._handle_scheduling(scheduled_time)

        # Make the API request
        async with session.post(
            f"{self.API_URL}/tweets",
            json=payload,
        ) as resp:
            if resp.status != 201:
                error = await resp.json()
                raise Exception(f"Twitter API error: {error}")
            
            return await resp.json()

    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
