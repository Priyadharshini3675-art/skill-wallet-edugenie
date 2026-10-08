"""Google Gemini SDK integration used by all EduGenie features."""
from __future__ import annotations
import logging, os, re
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / '.env', override=True)

class AIServiceError(Exception):
    """A safe error string suitable for the web UI."""

def valid_key():
    value = os.getenv('GEMINI_API_KEY','').strip()
    return bool(value and value not in ('YOUR_NEW_KEY_HERE', 'PASTE_YOUR_NEW_KEY_HERE') and len(value)>15)

@lru_cache(maxsize=1)
def _client():
    if not valid_key():
        raise AIServiceError('No Gemini key configured. Run Run_EduGenie.bat to configure a new key.')
    from google import genai
    return genai.Client(api_key=os.environ['GEMINI_API_KEY'].strip(), http_options={'timeout':60000})

def _classify_error(exc):
    raw=str(exc); low=raw.lower()
    status=getattr(exc,'code',None) or getattr(exc,'status_code',None)
    try: status=int(status)
    except (ValueError,TypeError):
        match=re.search(r'\b(400|401|403|404|429|500|503)\b',raw)
        status=int(match.group(1)) if match else 0
    if 'access_token_type_unsupported' in low:
        return 'Google rejected this key type (ACCESS_TOKEN_TYPE_UNSUPPORTED). Create a new Gemini key in Google AI Studio, and check the Google project and API access.'
    if 'api_key_invalid' in low or 'api key not valid' in low or 'invalid api key' in low:
        return 'Gemini API key invalid. Generate a NEW key in Google AI Studio and configure it through the launcher.'
    if status == 429: return 'Gemini rate limit or quota reached (429). Check usage and billing/quota in Google AI Studio.'
    if status == 404: return 'Gemini model not found (404) or not available for this account. Try another supported model in .env.'
    if status in (401,403): return f'Gemini rejected authentication or access ({status}). Verify the new key and its Google project permissions.'
    if status == 400: return 'Gemini rejected the request (400). Check the command window for the exact Google error; verify the API key and model in .env.'
    if status in (500,503): return f'Google Gemini service unavailable ({status}); please retry.'
    if 'timeout' in low or 'deadline' in low: return 'Gemini connection timed out; check network and try again.'
    return 'Gemini request failed ('+type(exc).__name__+'). See the terminal for a redacted diagnostic.'

def generate(prompt: str, *, json_output: bool=False, max_tokens: int=2048) -> str:
    if os.getenv('DEMO_MODE','false').lower()=='true':
        raise AIServiceError('DEMO_MODE is enabled. Set DEMO_MODE=false in .env.')
    if not valid_key():
        raise AIServiceError('Gemini API key missing. Double-click Run_EduGenie.bat to configure it.')
    from google.genai import types
    try:
        # Avoid model-specific thinking settings: older releases can return HTTP 400.
        config=types.GenerateContentConfig(
            temperature=0.2 if json_output else 0.5,
            max_output_tokens=max_tokens,
            **({'response_mime_type':'application/json'} if json_output else {})
        )
        model=os.getenv('GEMINI_MODEL','gemini-3.5-flash').strip() or 'gemini-3.5-flash'
        response=_client().models.generate_content(model=model,contents=prompt,config=config)
        answer=(response.text or '').strip()
        if not answer: raise AIServiceError('Google Gemini returned an empty response. Try another question or model.')
        return answer
    except AIServiceError: raise
    except Exception as exc:
        raw=str(exc).replace(os.getenv('GEMINI_API_KEY','') or '--placeholder--','[REDACTED]')
        raw=re.sub(r'(?i)(?:key=|x-goog-api-key[:=]\s*)[^\s&"\']+',r'key=[REDACTED]',raw)
        logging.getLogger('edugenie').error('Gemini error: %s',raw[:1100])
        raise AIServiceError(_classify_error(exc)) from exc
