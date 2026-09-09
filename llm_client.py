"""
Клієнт для роботи з OpenAI
"""
from openai import OpenAI
import json
import re

class LLMClient:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config['api_key'])
        self.model_name = config['model_name']
    
    def classify_request(self, text):
        """Класифікує запит та повертає структуровані дані"""
        prompt = self._build_prompt(text)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "Ти асистент для класифікації запитів. Відповідай лише JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config['temperature'],
                max_tokens=self.config['max_tokens']
            )
            
            return self._parse_response(response.choices[0].message.content)
        
        except Exception as e:
            raise Exception(f"Помилка при виклику OpenAI: {str(e)}")
    
    def _build_prompt(self, text):
        return f"""
Проаналізуй наступний запит від внутрішньої команди компанії Netpeak.

Текст запиту:
{text}

Визнач та поверни ТІЛЬКИ JSON з наступними полями:
{{
    "category": "одне з: автоматизація, інтеграція, звіт/аналітика, баг/підтримка, питання/консультація, поза скоупом",
    "target_department": "назва відділу або null",
    "priority": "low/medium/high",
    "short_summary": "суть запиту одним реченням (до 100 символів)",
    "requested_actions": ["список конкретних дій, які просять зробити"],
    "needs_clarification": true або false
}}

Правила:
- category: обирай зі списку
- priority: high — якщо є слова "терміново", "горить", "сьогодні", "ASAP"; low — якщо "не горить", "просто цікаво"
- requested_actions: перелічи дії, які просять виконати (наприклад: "створити звіт", "налаштувати інтеграцію", "полагодити баг")
- needs_clarification: true — якщо запит надто розмитий (наприклад: "треба бот", "нам би табличку")
- Якщо запит не стосується AI/автоматизації/технічних задач — став "поза скоупом"
- Відповідай лише JSON, без додаткових пояснень
"""
    
    def _parse_response(self, text):
        # Очищення від markdown
        text = text.strip()
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'```\s*$', '', text)
        text = text.strip()
        
        # Спроба знайти JSON якщо є зайвий текст
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group()
        
        return json.loads(text)