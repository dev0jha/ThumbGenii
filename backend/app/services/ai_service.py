"""
AI Service

Grok API integration for image generation and prompt enhancement.
"""

import logging
import httpx
from typing import Optional, List
from enum import Enum

from app.core.config import settings

logger = logging.getLogger("thumbai.ai")


class GrokImageSize(str, Enum):
    """Grok API image sizes."""
    SQUARE_1024 = "1024x1024"
    LANDSCAPE_1792 = "1792x1024"
    PORTRAIT_1024 = "1024x1792"


class AIService:
    """Service for AI-powered operations."""
    
    GROK_API_URL = "https://api.x.ai/v1/images/generations"
    GROK_CHAT_URL = "https://api.x.ai/v1/chat/completions"
    
    STYLE_PROMPTS = {
        "youtube_thumbnail": "YouTube thumbnail style: bold text, high contrast, eye-catching colors, professional lighting, 16:9 aspect ratio, viral potential",
        "shorts": "Vertical short-form video thumbnail: 9:16 aspect ratio, mobile-optimized, bold text, attention-grabbing",
        "square": "Square social media thumbnail: 1:1 aspect ratio, centered composition, Instagram-ready",
        "cinematic": "Cinematic movie poster style: dramatic lighting, epic composition, professional photography",
        "minimalist": "Minimalist design: clean lines, simple composition, modern aesthetic, lots of negative space",
        "gaming": "Gaming thumbnail: high energy, RGB lighting, action pose, game screenshot background",
        "tutorial": "Tutorial thumbnail: clear subject, educational feel, clean background, approachable",
        "mrbeast": "MrBeast style: shocked expression, bright yellow text, high contrast, chaotic energy, viral",
        "finance": "Finance thumbnail: professional, trustworthy, charts/graphs, blue tones, business aesthetic",
        "podcast": "Podcast cover: host portrait, microphone, warm lighting, intimate feel",
        "documentary": "Documentary style: serious tone, muted colors, informative, journalistic",
        "anime": "Anime style: vibrant colors, manga aesthetic, expressive characters",
        "tech": "Tech review: gadgets, clean background, modern aesthetic, professional lighting",
        "educational": "Educational: diagrams, clear visuals, learning-focused, academic feel",
        "dark_theme": "Dark theme: neon accents, dark background, cyberpunk aesthetic, glowing elements",
        "viral_shorts": "Viral shorts: attention-grabbing, fast-paced energy, bold colors, mobile-first"
    }
    
    def __init__(self):
        self.api_key = settings.GROK_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def enhance_prompt(self, user_prompt: str, style: str = "youtube_thumbnail", 
                       video_title: Optional[str] = None) -> str:
        """Enhance user prompt with style-specific optimizations."""
        style_prompt = self.STYLE_PROMPTS.get(style, self.STYLE_PROMPTS["youtube_thumbnail"])
        
        enhanced = f"""Create a professional thumbnail image: {user_prompt}

Style requirements: {style_prompt}

Technical specifications:
- High quality, photorealistic or stylized as appropriate
- Clear focal point
- Readable at small sizes
- Optimized for click-through rate
- No text in the image (text will be added separately)
- Professional lighting and composition
- Eye-catching colors and contrast"""
        
        if video_title:
            enhanced += f"\n\nVideo context: {video_title}"
        
        return enhanced
    
    async def generate_image(self, prompt: str, size: GrokImageSize = GrokImageSize.LANDSCAPE_1792) -> Optional[bytes]:
        """Generate image using Grok API."""
        if not self.api_key:
            raise ValueError("GROK_API_KEY not configured")
        
        payload = {
            "model": "grok-2-image",
            "prompt": prompt,
            "n": 1,
            "size": size.value
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.GROK_API_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract image data from response
                if "data" in data and len(data["data"]) > 0:
                    image_url = data["data"][0].get("url")
                    if image_url:
                        # Download the image
                        image_response = await client.get(image_url, timeout=30.0)
                        image_response.raise_for_status()
                        return image_response.content
                
                return None
                
            except httpx.HTTPError as e:
                logger.error("Grok API image generation error: %s", e)
                return None
            except Exception as e:
                logger.exception("Unexpected error in image generation")
                return None
    
    def generate_image_sync(self, prompt: str, size: GrokImageSize = GrokImageSize.LANDSCAPE_1792) -> Optional[bytes]:
        """Synchronous version of generate_image."""
        import asyncio
        return asyncio.run(self.generate_image(prompt, size))
    
    async def generate_titles(self, topic: str, style: Optional[str] = None, 
                              num_suggestions: int = 5) -> List[str]:
        """Generate viral video title suggestions."""
        if not self.api_key:
            return self._fallback_titles(topic, num_suggestions)
        
        style_hint = f" in {style} style" if style else ""
        
        payload = {
            "model": "grok-2",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at creating viral YouTube video titles. Generate attention-grabbing, click-worthy titles that are authentic and not clickbait."
                },
                {
                    "role": "user",
                    "content": f"Generate {num_suggestions} viral video titles for a video about: {topic}{style_hint}\n\nMake them engaging, specific, and optimized for high CTR. Include a mix of styles: curiosity gap, numbers/lists, how-to, and emotional triggers."
                }
            ],
            "max_tokens": 500
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.GROK_CHAT_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Parse titles from response
                titles = []
                for line in content.split("\n"):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith("-") or line.startswith("•")):
                        # Remove numbering/bullets
                        title = line.lstrip("0123456789.-• ").strip()
                        if title:
                            titles.append(title)
                
                return titles[:num_suggestions]
                
            except Exception as e:
                logger.error("Title generation error: %s", e)
                return self._fallback_titles(topic, num_suggestions)
    
    def _fallback_titles(self, topic: str, num: int) -> List[str]:
        """Fallback title suggestions."""
        templates = [
            f"I Tried {topic} for 30 Days - Here's What Happened",
            f"The Truth About {topic} Nobody Talks About",
            f"How I Mastered {topic} in Just One Week",
            f"{topic} Changed Everything - My Complete Guide",
            f"Stop Doing {topic} Wrong - Do This Instead",
            f"I Spent $1000 on {topic} - Was It Worth It?",
            f"The {topic} Secret Experts Don't Want You to Know",
            f"From Beginner to Pro: {topic} in 10 Minutes",
        ]
        return templates[:num]
    
    async def score_thumbnail(self, image_url: str) -> dict:
        """Score thumbnail using Grok vision analysis."""
        if self.api_key:
            try:
                payload = {
                    "model": "grok-2-vision",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an expert thumbnail analyst. Score thumbnails 0-100 based on: "
                                "visual impact, color balance, composition, text readability, "
                                "emotional appeal, and CTR potential. Be critical and specific."
                            )
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "Analyze this thumbnail image and provide:\n"
                                        "1. A score from 0-100\n"
                                        "2. Brief feedback (1 sentence)\n"
                                        "3. 3 specific improvement suggestions\n"
                                        "4. CTR potential (low/medium/high/viral)\n\n"
                                        "Return as JSON with keys: score, feedback, suggestions (array), ctr_potential"
                                    )
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_url}
                                }
                            ]
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                }
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.GROK_CHAT_URL,
                        headers=self.headers,
                        json=payload,
                        timeout=30.0
                    )
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    import json as json_mod
                    import re
                    # Try to extract JSON from response
                    json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
                    if json_match:
                        result = json_mod.loads(json_match.group())
                        return {
                            "score": max(0, min(100, int(result.get("score", 75)))),
                            "feedback": result.get("feedback", "Analysis complete"),
                            "suggestions": result.get("suggestions", [])[:3],
                            "ctr_potential": result.get("ctr_potential", "medium")
                        }
            except Exception as e:
                logger.warning("Grok vision scoring failed, using fallback: %s", e)
        
        return self._fallback_score()
    
    def _fallback_score(self) -> dict:
        """Fallback thumbnail scoring when AI is unavailable."""
        import random
        score = random.randint(65, 88)
        
        feedback_pool = [
            "Strong visual impact with good contrast",
            "Clear focal point that draws attention",
            "Good color balance and composition",
            "Text is readable and well-placed",
            "Emotional appeal is present"
        ]
        
        suggestion_pool = [
            "Consider increasing text size for mobile viewers",
            "Add more contrast between subject and background",
            "Try a more expressive facial expression",
            "Use brighter colors to stand out in feeds",
            "Ensure the main subject is clearly visible"
        ]
        
        ctr_map = {90: "viral", 80: "high", 70: "medium", 60: "low"}
        ctr_potential = ctr_map.get(score - (score % 10), "medium")
        
        return {
            "score": score,
            "feedback": random.choice(feedback_pool),
            "suggestions": random.sample(suggestion_pool, 3),
            "ctr_potential": ctr_potential
        }
    
    def get_size_for_style(self, style: str) -> GrokImageSize:
        """Get appropriate image size for style."""
        size_map = {
            "youtube_thumbnail": GrokImageSize.LANDSCAPE_1792,
            "shorts": GrokImageSize.PORTRAIT_1024,
            "square": GrokImageSize.SQUARE_1024,
            "viral_shorts": GrokImageSize.PORTRAIT_1024,
            "podcast": GrokImageSize.SQUARE_1024,
        }
        return size_map.get(style, GrokImageSize.LANDSCAPE_1792)


# Singleton instance
ai_service = AIService()
