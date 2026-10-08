"""Configure a new Gemini API key locally. Keys are never bundled in the ZIP."""
from __future__ import annotations
import getpass,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ENV=ROOT/'.env'

def read_env():
    found={}
    if ENV.exists():
        for line in ENV.read_text(encoding='utf-8-sig').splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                k,v=line.split('=',1);found[k.strip()]=v.strip().strip('"').strip("'")
    return found

def main():
    previous=read_env()
    print('\nEduGenie / Google Gemini setup')
    print('Create a fresh key at https://aistudio.google.com/apikey')
    print('Important: never paste the key into chat or upload the .env file.')
    key=previous.get('GEMINI_API_KEY','')
    if key and previous.get('DEMO_MODE','false').lower()!='true':
        print('A saved key is present. Press Enter to reuse it, or type R to replace it.')
        try: replace=input('Reuse key? [Enter=reuse, R=replace]: ').strip().lower()
        except EOFError: return 1
    else: replace='r'
    if replace=='r' or not key:
        try: key=getpass.getpass('Paste your NEW Google AI Studio key (hidden): ').strip()
        except (EOFError,KeyboardInterrupt):return 1
        if not key or any(x in key for x in [' ', '\n','\r','=']):
            print('No valid key provided. Setup stopped.');return 1
    model=previous.get('GEMINI_MODEL') or 'gemini-3.5-flash'
    print('Using Gemini model:',model)
    ENV.write_text('GEMINI_API_KEY='+key+'\nGEMINI_MODEL='+model+'\nDEMO_MODE=false\n',encoding='utf-8')
    try:os.chmod(ENV,0o600)
    except OSError:pass
    print('Configuration saved. Checking Google Gemini connection...')
    # Fresh process, settings will be loaded from the new .env.
    try:
        from ai_client import generate
        result=generate('Reply with the word READY only.',max_tokens=100)
        print('[SUCCESS] Gemini responded:',result[:100])
    except Exception as exc:
        print('[WARNING] Gemini connection test failed:',str(exc))
        print('The server will still start. Check the error and update your key/model before asking questions.')
    return 0

if __name__=='__main__':sys.exit(main())
