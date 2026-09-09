"""
Генерація звітів у різних форматах
"""
import pandas as pd
from datetime import datetime

class ReportGenerator:
    def __init__(self, results):
        self.results = results
        self.df = pd.DataFrame(results)
    
    def generate_aggregates(self):
        """Генерує агреговану статистику"""
        category_counts = self.df['category'].value_counts()
        priority_counts = self.df['priority'].value_counts()
        dept_counts = self.df['target_department'].value_counts()
        clarification_needed = self.df[self.df['needs_clarification'] == True]
        
        return {
            'by_category': category_counts.to_dict(),
            'by_priority': priority_counts.to_dict(),
            'by_department': dept_counts.to_dict(),
            'needs_clarification': clarification_needed.to_dict('records'),
            'total_requests': len(self.df),
            'needs_clarification_count': len(clarification_needed),
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def save_markdown(self, filename):
        """Зберігає звіт у Markdown"""
        agg = self.generate_aggregates()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 📊 Звіт про класифікацію запитів\n\n")
            f.write(f"**Дата генерації:** {agg['generated_at']}\n\n")
            f.write(f"**Всього запитів:** {agg['total_requests']}\n\n")
            
            # Категорії
            f.write("## 📂 Розподіл за категоріями\n\n")
            if agg['by_category']:
                for cat, count in sorted(agg['by_category'].items(), key=lambda x: x[1], reverse=True):
                    pct = count / agg['total_requests'] * 100
                    f.write(f"- **{cat}**: {count} ({pct:.1f}%)\n")
            else:
                f.write("Немає даних\n")
            
            # Пріоритети
            f.write("\n## ⚡ Розподіл за пріоритетом\n\n")
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            if agg['by_priority']:
                for prior in sorted(agg['by_priority'].keys(), key=lambda x: priority_order.get(x, 3)):
                    count = agg['by_priority'][prior]
                    pct = count / agg['total_requests'] * 100
                    emoji = '🔴' if prior == 'high' else '🟡' if prior == 'medium' else '🟢'
                    f.write(f"- {emoji} **{prior}**: {count} ({pct:.1f}%)\n")
            else:
                f.write("Немає даних\n")
            
            # Відділи
            f.write("\n## 🏢 Розподіл за відділами\n\n")
            if agg['by_department']:
                for dept, count in sorted(agg['by_department'].items(), key=lambda x: x[1], reverse=True):
                    pct = count / agg['total_requests'] * 100
                    dept_name = dept if dept else 'Не визначено'
                    f.write(f"- **{dept_name}**: {count} ({pct:.1f}%)\n")
            else:
                f.write("Немає даних\n")
            
            # Запити що потребують уточнення
            f.write(f"\n## ❓ Запити, що потребують уточнення ({agg['needs_clarification_count']})\n\n")
            if agg['needs_clarification']:
                for req in agg['needs_clarification']:
                    f.write(f"- **{req.get('id')}** ({req.get('channel')}): {req.get('short_summary')}\n")
            else:
                f.write("Всі запити зрозумілі та можуть бути взяті в роботу ✅\n")
    
    def save_csv(self, filename):
        """Зберігає звіт у CSV"""
        columns = ['id', 'channel', 'timestamp', 'category', 'priority', 
                   'target_department', 'short_summary', 'needs_clarification']
        df_report = self.df[columns].copy()
        df_report.to_csv(filename, index=False, encoding='utf-8-sig')