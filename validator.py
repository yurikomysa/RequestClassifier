"""
Валідація та нормалізація відповідей LLM
"""
from typing import Dict, Any

class ResponseValidator:
    CATEGORIES = [
        'автоматизація', 
        'інтеграція', 
        'звіт/аналітика', 
        'баг/підтримка', 
        'питання/консультація', 
        'поза скоупом'
    ]
    
    PRIORITIES = ['low', 'medium', 'high']
    
    def validate(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Валідує та нормалізує відповідь від LLM"""
        
        # Категорія
        category = response.get('category', 'поза скоупом')
        if category not in self.CATEGORIES:
            category = 'поза скоупом'
        
        # Відділ
        dept = response.get('target_department')
        if dept is not None and not isinstance(dept, str):
            dept = None
        if dept and len(dept.strip()) == 0:
            dept = None
        
        # Пріоритет
        priority = response.get('priority', 'medium')
        if priority not in self.PRIORITIES:
            priority = 'medium'
        
        # Короткий опис
        summary = response.get('short_summary', '')
        if not summary or len(summary.strip()) < 3:
            summary = 'Запит потребує уточнення'
        summary = summary.strip()[:200]
        
        # Запитувані дії
        actions = response.get('requested_actions', [])
        if not isinstance(actions, list):
            actions = []
        actions = [str(a).strip() for a in actions if str(a).strip()]
        actions = actions[:5]
        
        # Чи потрібне уточнення
        needs_clar = response.get('needs_clarification', False)
        if isinstance(needs_clar, str):
            needs_clar = needs_clar.lower() in ['true', '1', 'yes']
        needs_clar = bool(needs_clar)
        
        return {
            'category': category,
            'target_department': dept,
            'priority': priority,
            'short_summary': summary,
            'requested_actions': actions,
            'needs_clarification': needs_clar
        }