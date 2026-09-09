"""
Конфігурація проєкту
"""
import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    provider = os.getenv('LLM_PROVIDER', 'openai').lower()
    
    config = {
        'llm_provider': provider,
        'temperature': 0.1,
        'max_tokens': 1024,
    }
    
    if provider == 'openai':
        config['api_key'] = os.getenv('OPENAI_API_KEY')
        config['model_name'] = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
    else:
        raise ValueError(f"Невідомий провайдер: {provider}")
    
    if not config['api_key']:
        raise ValueError(f"API ключ для {provider} не знайдено. Перевірте .env файл")
    
    return config