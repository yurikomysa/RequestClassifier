"""
Обробка окремого запиту
"""
from datetime import datetime

class RequestProcessor:
    def __init__(self, llm_client, validator):
        self.llm = llm_client
        self.validator = validator
    
    def process_request(self, request_id, channel, timestamp, raw_text):
        try:
            # Виклик LLM
            llm_response = self.llm.classify_request(raw_text)
        except Exception as e:
            # Fallback при помилці
            print(f"Помилка: {str(e)}")
            llm_response = {
                'category': 'поза скоупом',
                'target_department': None,
                'priority': 'medium',
                'short_summary': 'Помилка обробки',
                'requested_actions': [],
                'needs_clarification': True
            }
        
        # Валідація та нормалізація
        validated = self.validator.validate(llm_response)
        
        # Додавання метаданих
        return {
            'id': request_id,
            'channel': channel,
            'timestamp': timestamp,
            'raw_text': raw_text,
            'processed_at': datetime.now().isoformat(),
            **validated
        }