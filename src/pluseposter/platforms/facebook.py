from typing import Dict, Any, Optional, List, Tuple, Deque
from datetime import datetime, timedelta
import aiohttp
import asyncio
import logging
import time
from collections import deque
from functools import lru_cache
from heapq import heappush, heappop
from facebook import GraphAPI
from .base import Platform


class RateLimiter:
    """Token bucket rate limiter implementation"""
    def __init__(self, rate: int, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity  # max tokens in bucket
        self.tokens = capacity
        self.last_update = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> float:
        """Acquire tokens, waiting if necessary"""
        async with self._lock:
            now = time.monotonic()
            time_passed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + time_passed * self.rate)
            self.last_update = now
            
            if tokens > self.capacity:
                raise ValueError("Requested tokens exceed capacity")
                
            if self.tokens < tokens:
                sleep_time = (tokens - self.tokens) / self.rate
                await asyncio.sleep(sleep_time)
                return await self.acquire(tokens)
                
            self.tokens -= tokens
            return 0

class ConnectionPool:
    """Connection pool for HTTP sessions"""
    def __init__(self, size: int = 10):
        self.size = size
        self._pool: Deque[aiohttp.ClientSession] = deque()
        self._lock = asyncio.Lock()
        
    async def get_session(self) -> aiohttp.ClientSession:
        """Get a session from the pool"""
        async with self._lock:
            if self._pool:
                return self._pool.popleft()
            return aiohttp.ClientSession()
            
    async def release_session(self, session: aiohttp.ClientSession):
        """Return a session to the pool"""
        async with self._lock:
            if len(self._pool) < self.size:
                self._pool.append(session)
            else:
                await session.close()

class FacebookPlatform(Platform):
    """
    Facebook platform implementation using facebook-sdk with advanced features:
    - Connection pooling
    - Rate limiting
    - Request retry with exponential backoff
    - LRU caching for media uploads
    - Batch processing
    - Priority queue for scheduled posts
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.logger = logging.getLogger("pluseposter.facebook")
        self.graph = None
        self.rate_limiter = RateLimiter(rate=5, capacity=10)  # 5 requests per second, burst of 10
        self.connection_pool = ConnectionPool(size=10)
        self._scheduled_posts = []  # min-heap for scheduled posts
        self._scheduled_lock = asyncio.Lock()
        self._ensure_graph()
        
        # Start background task for processing scheduled posts
        self._scheduled_task = asyncio.create_task(self._process_scheduled_posts())

    def _ensure_graph(self):
        """Initialize or get Facebook Graph API instance"""
        if not self.graph:
            self.graph = GraphAPI(access_token=self.config.api_key)

    @lru_cache(maxsize=128)
    async def _upload_media(self, file_path: str, media_type: str) -> str:
        """
        Upload media to Facebook with caching and retry logic
        
        Args:
            file_path (str): Path to media file
            media_type (str): Type of media (image, video)
            
        Returns:
            str: Media ID from Facebook
        """
        max_retries = 3
        base_delay = 1.0  # Start with 1 second delay
        
        for attempt in range(max_retries):
            try:
                await self.rate_limiter.acquire()
                session = await self.connection_pool.get_session()
                
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
                finally:
                    await self.connection_pool.release_session(session)
                    
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    self.logger.error(f"Facebook media upload failed after {max_retries} attempts: {str(e)}")
                    raise
                    
                # Exponential backoff
                delay = base_delay * (2 ** attempt)
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s: {str(e)}")
                await asyncio.sleep(delay)

    async def _process_scheduled_posts(self):
        """Background task to process scheduled posts"""
        while True:
            try:
                now = datetime.utcnow()
                
                async with self._scheduled_lock:
                    # Process all posts that are due
                    while self._scheduled_posts and self._scheduled_posts[0][0] <= now:
                        scheduled_time, post_data = heappop(self._scheduled_posts)
                        asyncio.create_task(self._post_impl(**post_data))
                
                # Sleep until the next scheduled post or 60 seconds
                next_run = 60.0  # Default sleep time in seconds
                if self._scheduled_posts:
                    next_run = max(0, (self._scheduled_posts[0][0] - datetime.utcnow()).total_seconds())
                
                await asyncio.sleep(min(1.0, next_run))  # Check at least every second
                
            except Exception as e:
                self.logger.error(f"Error in scheduled posts processor: {str(e)}")
                await asyncio.sleep(5)  # Prevent tight loop on errors

    async def post_batch(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Post multiple contents in a batch
        
        Args:
            posts: List of post dictionaries with content_type, content, caption, scheduled_time
            
        Returns:
            List of results from each post
        """
        tasks = [self.post(**post) for post in posts]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _post_impl(
        self,
        content_type: str,
        content: Any,
        caption: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Internal implementation of post with retry logic"""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                await self.rate_limiter.acquire()
                session = await self.connection_pool.get_session()
                
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
                        "post_id": result.get('id'),
                        "caption": caption,
                    }
                        
                finally:
                    await self.connection_pool.release_session(session)
                    
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    self.logger.error(f"Facebook post failed after {max_retries} attempts: {str(e)}")
                    raise
                    
                # Exponential backoff
                delay = base_delay * (2 ** attempt)
                self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.1f}s: {str(e)}")
                await asyncio.sleep(delay)

    async def post(
        self,
        content_type: str,
        content: Any,
        caption: Optional[str] = None,
        scheduled_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Post content to Facebook with scheduling support
        
        Args:
            content_type (str): Type of content (text, image, video)
            content (Any): Content to post
            caption (Optional[str]): Caption for the post
            scheduled_time (Optional[datetime]): UTC time to schedule the post
            
        Returns:
            Dict[str, Any]: Response from Facebook API or scheduling confirmation
        """
        if not self._validate_content(content_type, content):
            raise ValueError("Invalid content")
            
        post_data = {
            'content_type': content_type,
            'content': content,
            'caption': caption,
        }
        
        if scheduled_time:
            # Convert to UTC naive datetime if timezone-aware
            if scheduled_time.tzinfo is not None:
                scheduled_time = scheduled_time.astimezone(timezone.utc).replace(tzinfo=None)
                
            if scheduled_time < datetime.utcnow():
                raise ValueError("Scheduled time must be in the future")
                
            async with self._scheduled_lock:
                heappush(self._scheduled_posts, (scheduled_time, post_data))
                
            return {
                "success": True,
                "scheduled": True,
                "scheduled_time": scheduled_time.isoformat(),
                "message": "Post scheduled successfully"
            }
            
        return await self._post_impl(**post_data)

    async def close(self):
        """Clean up resources"""
        if hasattr(self, '_scheduled_task'):
            self._scheduled_task.cancel()
            try:
                await self._scheduled_task
            except asyncio.CancelledError:
                pass
                
        if hasattr(self, 'connection_pool'):
            # Close all sessions in the connection pool
            while self.connection_pool._pool:
                session = self.connection_pool._pool.popleft()
                await session.close()
        self.graph = None
