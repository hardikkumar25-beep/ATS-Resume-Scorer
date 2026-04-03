import json
import re
from typing import Dict, Any, Optional

def parse_ats_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Parse ATS scorer JSON response
    
    Handles both:
    - Pure JSON
    - JSON wrapped in markdown code blocks
    - JSON with text before/after
    """
    
    try:
        # Try direct JSON parse first
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, response_text, re.DOTALL)
    
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try to find raw JSON in text
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    match = re.search(json_pattern, response_text, re.DOTALL)
    
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    
    print(f"❌ Failed to parse JSON from response")
    return None


def extract_score_data(parsed_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract relevant fields for database storage
    """
    
    return {
        'overall_score': parsed_json.get('total_score', 0),
        'technical_skills_score': parsed_json.get('breakdown', {}).get('required_skills', 0) + 
                                   parsed_json.get('breakdown', {}).get('preferred_skills', 0),
        'experience_score': parsed_json.get('breakdown', {}).get('experience', 0),
        'education_score': parsed_json.get('breakdown', {}).get('education', 0),
        'project_relevance_score': parsed_json.get('breakdown', {}).get('additional', 0),
        'matching_skills': [item['skill'] for item in parsed_json.get('matched_skills_detail', [])],
        'missing_skills': parsed_json.get('missing_skills', []),
        'recommendations': parsed_json.get('recommendations', ''),
        'classification': parsed_json.get('classification', ''),
        'matched_required': parsed_json.get('matched_required', 0),
        'total_required': parsed_json.get('total_required', 0),
        'matched_preferred': parsed_json.get('matched_preferred', 0),
        'total_preferred': parsed_json.get('total_preferred', 0)
    }