# OpenAI GPT Integration

Этот проект включает интеграцию с OpenAI API для использования GPT-4 и GPT-3.5-turbo.

## Установка

### 1. Получите API ключ
- Перейдите на https://platform.openai.com/api-keys
- Создайте новый API ключ
- Скопируйте его в безопасное место

### 2. Настройка окружения

```bash
cp .env.example .env
# Отредактируйте .env и добавьте ваш API ключ
```

## Использование

### Python
```bash
cd python
pip install -r requirements.txt
python gpt_integration.py
```

### JavaScript/Node.js
```bash
cd javascript
npm install
node gpt-integration.js
```

### TypeScript
```bash
cd typescript
npm install
npm run build
node dist/gpt-integration.js
```

## Примеры

See examples in each language-specific directory.
