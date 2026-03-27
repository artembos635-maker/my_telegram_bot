def ask_ai(msg, name):
    """Запрос к OpenRouter (бесплатная модель)"""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-7b-instruct",  # 🔥 БЕСПЛАТНАЯ МОДЕЛЬ
                "messages": [
                    {"role": "system", "content": f"Ты дружелюбный помощник по имени Губаты. Общаешься с {name}. Отвечай кратко и дружелюбно."},
                    {"role": "user", "content": msg}
                ],
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response.status_code != 200:
            return f"😕 Ошибка API: {response.status_code}"
        
        data = response.json()
        return data['choices'][0]['message']['content']
        
    except Exception as e:
        return f"😵 Ошибка: {e}"
