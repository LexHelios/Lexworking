#!/usr/bin/env python3
"""
Media Generation Agent for OMNIPOTENT System
"""

from omnipotent_agents.unrestricted_image_agent import UnrestrictedImageAgent

class MediaGenerationAgent:
    """Media generation agent with unrestricted capabilities"""
    
    def __init__(self, config):
        self.config = config
        self.image_agent = UnrestrictedImageAgent()
    
    async def generate_image(self, request):
        """Generate images using unrestricted models"""
        return await self.image_agent.generate_educational_image(
            prompt=request,
            style="medical_textbook",
            model_preference="flux-dev-uncensored"
        )