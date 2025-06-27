from typing import Dict, Any, Optional
from datetime import datetime
import aiohttp
import logging
from facebook import GraphAPI
from .base import Platform


class FacebookPlatform(Platform):
    """
    Facebook platform implementation using facebook-sdk
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger("pluseposter.facebook")
        self.graph = None
        self._ensure_graph()

    def _ensure_graph(self):
        """Initialize or get Facebook Graph API instance"""
        if not self.graph:
            self.graph = GraphAPI(access_token=self.config.api_key)

    async def _upload_media(self, file_path: str, media_type: str) -> str:
        """
        Upload media to Facebook
        
        Args:
            file_path (str): Path to media file
            media_type (str): Type of media (image, video)
            
        Returns:
            str: Media ID from Facebook
        """
        try:
            with open(file_path, 'rb') as f:
                if media_type == "image":
                    result = self.graph.put_photo(
                        image=f,
                        published=False
                    )
                else:  # video
                    result = self.graph.put_video(
                        video_file=f,
                        published=False
                    )
                return result['id']
        except Exception as e:
            self.logger.error(f"Facebook media upload failed: {str(e)}")
            raise

    async def post(
        self,
        content_type: str,
        content: Any,
        caption: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Post content to Facebook
        
        Args:
            content_type (str): Type of content (text, image, video)
            content (Any): Content to post
            caption (Optional[str]): Caption for the post
            scheduled_time (Optional[datetime]): Time to schedule the post
            
        Returns:
            Dict[str, Any]: Response from Facebook API
        """
        if not self._validate_content(content_type, content):
            raise ValueError("Invalid content")

        try:
            if content_type == "text":
                result = self.graph.put_object(
                    parent_object='me',
                    connection_name='feed',
                    message=caption
                )

            elif content_type in ["image", "video"]:
                file_path = validate_file_path(content)
                media_id = await self._upload_media(file_path, content_type)
                
                result = self.graph.put_object(
                    parent_object='me',
                    connection_name='feed',
                    message=caption,
                    attached_media=[{"media_fbid": media_id}]
                )

            else:
                raise ValueError(f"Unsupported content type: {content_type}")

            return {
                "success": True,
                "post_id": result['id'],
                "caption": caption,
            }

        except Exception as e:
            self.logger.error(f"Facebook post failed: {str(e)}")
            raise

    async def close(self):
        """Close Facebook session"""
        self.graph = None
