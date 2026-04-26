"""
Utility functions for parsing AI responses.
"""
import json
import re
from typing import Dict, Any, Optional


class ResponseParser:
    """Parse Claude AI responses."""
    
    @staticmethod
    def extract_json(response_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from response text.
        
        Args:
            response_text: Raw response from Claude
            
        Returns:
            Parsed JSON as dictionary or None
        """
        try:
            # Find JSON block
            json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try finding JSON directly
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                else:
                    return None
            
            return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError):
            return None
    
    @staticmethod
    def extract_markdown_block(response_text: str, language: str = "") -> Optional[str]:
        """
        Extract content from markdown code block.
        
        Args:
            response_text: Raw response text
            language: Code block language identifier
            
        Returns:
            Content of the code block or None
        """
        try:
            pattern = f'```{language}\n(.*?)\n```'
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                return match.group(1)
            return None
        except Exception:
            return None
    
    @staticmethod
    def clean_response(response_text: str) -> str:
        """
        Clean response text by removing markdown formatting.
        
        Args:
            response_text: Raw response text
            
        Returns:
            Cleaned response text
        """
        # Remove markdown code blocks
        response_text = re.sub(r'```[\w]*\n?', '', response_text)
        # Remove extra whitespace
        response_text = '\n'.join(line.strip() for line in response_text.split('\n') if line.strip())
        return response_text.strip()
