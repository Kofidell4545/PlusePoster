import argparse
import asyncio
from datetime import datetime
import logging
from pathlib import Path
from typing import Optional
from .pluseposter import PlusePoster
from .utils import setup_logging

def parse_args() -> argparse.Namespace:
    """
    📱 Parse command line arguments
    
    This function sets up the command line interface with all available options.
    Each argument is clearly documented to help users understand how to use the CLI.
    """
    parser = argparse.ArgumentParser(
        description="🚀 PlusePoster CLI - Automate your social media posts!"
    )
    
    # Platform selection
    parser.add_argument(
        "--platform",
        required=True,
        choices=["twitter", "instagram", "facebook"],
        help="""
        🌐 Select which social media platform to post to:
        - twitter: Post to Twitter/X
        - instagram: Post to Instagram
        - facebook: Post to Facebook
        """
    )
    
    # Content type
    parser.add_argument(
        "--type",
        required=True,
        choices=["text", "image", "video"],
        help="""
        📝 Type of content to post:
        - text: Just text message
        - image: Image file
        - video: Video file
        """
    )
    
    # Caption
    parser.add_argument(
        "--caption",
        help="""
        ✍️ Add a caption to your post (required for media uploads)
        - For text posts: This is your message
        - For media: This will be the description
        """
    )
    
    # File path
    parser.add_argument(
        "--file",
        help="""
        📁 Path to your media file (required for image/video):
        - For images: Path to image file (jpg, png)
        - For videos: Path to video file
        """
    )
    
    # Scheduling
    parser.add_argument(
        "--schedule",
        help="""
        📅 Schedule your post for a future time:
        - Format: YYYY-MM-DDTHH:MM:SS
        - Example: 2025-07-01T09:00:00Z
        """
    )
    
    # Debug mode
    parser.add_argument(
        "--debug",
        action="store_true",
        help="""
        🔍 Enable debug mode for detailed logging
        - Shows more detailed information about what's happening
        - Useful for troubleshooting
        """
    )
    
    return parser.parse_args()

async def main():
    """Main function"""
    args = parse_args()
    setup_logging(args.debug)
    
    # Initialize PlusePoster
    poster = PlusePoster()
    
    # Prepare content
    content = args.file if args.type in ["image", "video"] else args.caption
    
    # Convert schedule time if provided
    scheduled_time = datetime.fromisoformat(args.schedule) if args.schedule else None
    
    try:
        # Post or schedule the content
        result = await poster.post(
            platform=args.platform,
            content_type=args.type,
            content=content,
            caption=args.caption,
            scheduled_time=scheduled_time,
        )
        print(f"Success! Response: {result}")
    except Exception as e:
        logging.error(f"Error posting content: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
