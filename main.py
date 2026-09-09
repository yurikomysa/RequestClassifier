"""
Головний скрипт запуску
"""
import json
import pandas as pd
from config import load_config
from llm_client import LLMClient
from request_processor import RequestProcessor
from validator import ResponseValidator
from report_generator import ReportGenerator

def main():
    print("🚀 Запуск RequestClassifier...")
    
    # 1. Завантаження конфігурації
    config = load_config()
    print(f"✅ Використовується LLM: {config['llm_provider']} ({config['model_name']})")
    
    # 2. Ініціалізація компонентів
    llm_client = LLMClient(config)
    validator = ResponseValidator()
    processor = RequestProcessor(llm_client, validator)
    
    # 3. Читання даних
    print("📖 Читання input_requests.csv...")
    df = pd.read_csv('input_requests.csv')
    print(f"✅ Знайдено {len(df)} запитів")
    
    # 4. Обробка запитів
    print("🔄 Обробка запитів через LLM...")
    results = []
    for idx, row in df.iterrows():
        print(f"   Обробка {row['id']}...", end=" ")
        result = processor.process_request(
            request_id=row['id'],
            channel=row['channel'],
            timestamp=row['timestamp'],
            raw_text=row['raw_text']
        )
        results.append(result)
        print(f"✅ {result['category']} | {result['priority']}")
    
    # 5. Збереження результатів
    print("💾 Збереження результатів...")
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("✅ output.json збережено")
    
    # 6. Генерація звіту
    print("📊 Генерація звіту...")
    report_gen = ReportGenerator(results)
    report_gen.save_markdown('report.md')
    report_gen.save_csv('report.csv')
    print("✅ report.md та report.csv збережено")
    
    print("\n✅ Готово! Перегляньте результати в output.json та report.md")

if __name__ == "__main__":
    main()