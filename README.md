# RequestClassifier — автоматична класифікація запитів

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5--turbo-green.svg)](https://openai.com/)

## 📋 Опис

Сервіс для автоматичної класифікації вхідних запитів від внутрішніх команд Netpeak.
Замінює ручну обробку запитів з Slack, Telegram та Email на автоматизовану систему.

**Що визначає:**

- **Категорію**: автоматизація, інтеграція, звіт/аналітика, баг/підтримка, питання/консультація, поза скоупом
- **Відділ-замовник**: маркетинг, продажі, аналітика, HR, SMM, контент, технічний, підтримка
- **Пріоритет**: high/medium/low (на основі тону та змісту)
- **Суть запиту**: коротке резюме одним реченням
- **Запитувані дії**: список конкретних дій, які просять виконати
- **Необхідність уточнення**: чи запит достатньо чіткий для роботи

---

## 🚀 Як запустити

### 1. Клонуйте репозиторій

```bash
git clone <repository-url>
cd RequestClassifier
```

### 2. Створіть віртуальне середовище

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate     # Windows
```

### 3. Встановіть залежності

```bash
pip install -r requirements.txt
```

### 4. Налаштуйте змінні середовища

Створіть файл `.env` у корені проекту:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-ваш_ключ_тут
MODEL_NAME=gpt-3.5-turbo
```

> 💡 **Як отримати API ключ:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 5. Підготуйте вхідні дані

Файл `input_requests.csv` має містити колонки:

- `id` — унікальний ідентифікатор
- `channel` — Slack/Telegram/Email
- `timestamp` — час отримання
- `raw_text` — текст запиту

Приклад вже включений у репозиторій.

### 6. Запустіть обробку

```bash
python main.py
```

### 7. Отримайте результати

- `output.json` — повна структурована інформація по кожному запиту
- `report.md` — агрегований звіт з розподілами у Markdown
- `report.csv` — звіт у CSV для аналізу в Excel

---

## 📤 Приклад результату

**output.json:**

```json
[
  {
    "id": "REQ-001",
    "channel": "Slack",
    "timestamp": "2026-06-08 09:14",
    "raw_text": "Привіт! Можна автоматизувати...",
    "processed_at": "2026-06-09T12:30:45.123456",
    "category": "автоматизація",
    "target_department": "маркетинг",
    "priority": "medium",
    "short_summary": "Автоматизувати щотижневий звіт по Google Ads",
    "requested_actions": [
      "налаштувати автоматичний збір метрик",
      "створити шаблон звіту"
    ],
    "needs_clarification": false
  }
]
```

**report.md:**

- Розподіл за категоріями з відсотками
- Розподіл за пріоритетами з емодзі (🔴 high, 🟡 medium, 🟢 low)
- Розподіл за відділами
- Список запитів, що потребують уточнення

---

## ⚠️ Обмеження рішення

### 1. Невалідний вивід LLM

**Проблема:** LLM може повернути невалідний JSON, неправильні категорії або пропущені поля.

**Рішення:**

- У `validator.py` реалізовано валідацію всіх полів з fallback-значеннями:
  - `category` → `"поза скоупом"` (якщо не зі списку)
  - `priority` → `"medium"` (якщо не low/medium/high)
  - `needs_clarification` → `True` (якщо не boolean)
  - `requested_actions` → `[]` (якщо не список)
- У `llm_client.py` є парсинг з очищенням від markdown та пошуком JSON у тексті
- При повній помилці LLM — використовується fallback-схема

**Як закрито:** ✅ Повна валідація з дефолтними значеннями гарантує, що програма не впаде.

---

### 2. Великий обсяг даних

**Проблема:** При 1000+ запитів послідовна обробка може зайняти години.

**Рішення:**

- Використовується послідовна обробка (один запит за раз)
- Додано прогресс-бар у консолі

**Як закрито:** ⚠️ Частково. Для продакшену потрібна асинхронна обробка або batch-запити.

**Що можна зробити:**

```python
# Асинхронна версія (не реалізовано в цьому релізі)
async def process_batch(requests):
    tasks = [process_request(req) for req in requests]
    return await asyncio.gather(*tasks)
```

---

### 3. Недетермінізм LLM

**Проблема:** При однакових вхідних даних LLM може давати різні результати.

**Рішення:**

- Встановлено `temperature=0.1` у `config.py` (мінімальна креативність)
- Чіткі інструкції в промпті з обмеженим вибором категорій

**Як закрито:** ✅ Значно знижено недетермінізм, але 100% детермінізму досягти неможливо через природу LLM.

---

### 4. Вартість токенів

**Проблема:** Кожен запит до LLM коштує грошей.

**Розрахунки:**

- **GPT-3.5-turbo**: $0.002 за 1000 вхідних токенів + $0.002 за 1000 вихідних
- Середній запит: ~500 вхідних токенів + ~100 вихідних = ~0.6 токенів/запит
- **Вартість на 1 запит**: ~$0.0000012
- **Для 1000 запитів**: ~$0.0012

**Як закрито:** ⚠️ Вартість мінімальна, але для великих обсягів потрібно:

- Використовувати кешування однакових запитів
- Перейти на локальні моделі (наприклад, Llama 3)

---

### 5. Обробка помилок API

**Проблема:** OpenAI API може бути недоступне або повертати помилки.

**Рішення:**

- У `request_processor.py` реалізовано try/except з fallback-значеннями
- При помилці API — запит позначається як `needs_clarification: true`

**Як закрито:** ✅ Програма не падає при помилках API.

---

## 🚧 Що зробив би далі (якби було більше часу)

### 1. Асинхронна обробка ⚡

```python
# Замість послідовної обробки
for row in df.iterrows():  # повільно
    process(row)

# Використовувати asyncio + aiohttp
async def process_all(requests):
    tasks = [process_request(req) for req in requests]
    return await asyncio.gather(*tasks)
```

### 2. Кешування відповідей 💾

```python
# Зберігати результати для однакових запитів
cache = {}
if text in cache:
    return cache[text]
result = llm.classify(text)
cache[text] = result
```

### 3. REST API (FastAPI) 🌐

```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/classify")
async def classify(request: Request):
    return processor.process_request(request)
```

### 4. Docker-образ 🐳

```dockerfile
FROM python:3.9
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

### 5. Логування та моніторинг 📊

```python
import logging
logging.basicConfig(level=logging.INFO)
logger.info(f"Оброблено {len(results)} запитів")
```

### 6. Fine-tuning моделі 🎯

- Зібрати датасет з правильно розмічених запитів
- Донавчити GPT-3.5 на цих даних
- Підвищити точність класифікації

### 7. Telegram бот 🤖

- Автоматичне надсилання дайджесту в Telegram
- Інтерактивне уточнення розмитих запитів

### 8. Google Sheets інтеграція 📝

- Автоматичний експорт результатів у Google Sheets
- Спільний доступ для команди

### 9. Human-in-the-loop 👤

- Ручне уточнення запитів з `needs_clarification: true`
- Збір фідбеку для покращення моделі

### 10. Тести та CI/CD 🧪

```python
# pytest тести
def test_validator():
    assert validator.validate({})['category'] == 'поза скоупом'
```

---

## 📁 Структура проекту

```
RequestClassifier/
├── README.md                 # Цей файл
├── requirements.txt          # Залежності
├── .env.example              # Приклад конфігурації
├── .gitignore                # Ігноровані файли
├── main.py                   # Головний скрипт
├── config.py                 # Конфігурація
├── llm_client.py             # Клієнт OpenAI
├── request_processor.py      # Обробка запитів
├── validator.py              # Валідація даних
├── report_generator.py       # Генерація звітів
└── input_requests.csv        # Вхідні дані
```

---

## 🛠 Технології

- **Python 3.8+**
- **OpenAI API** (GPT-3.5-turbo)
- **Pandas** — робота з даними
- **Python-dotenv** — змінні середовища

---

## 📝 Ліцензія

Цей проект створено в рамках тестового завдання для **Netpeak (AI Solutions)**.

---

## 👤 Контакти

- **Автор:** Yuri Komysa
- **Email:** yurikomysa@gmail.com
- **GitHub:** [github.com/yurikomysa/RequestClassifier](https://github.com/yurikomysa/RequestClassifier)

---

**Дякую за увагу! 🚀**
