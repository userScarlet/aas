import os
import requests
from telebot import TeleBot

TOKEN = "8998319147:AAEMBPz3apnk8tw2vQEtono9M07Idr8YKvE"
HF_TOKEN = "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" 

bot = TeleBot(TOKEN)

CUSTOM_PROMPT = (
    "Transform the motorcycle from the photo into a supermoto. "
    "Replace both wheels with 17-inch supermoto wheels (17/17 size), "
    "black slick tires, alloy rims matched to the motorcycle's color scheme, "
    "high quality, detailed, realistic."
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Привет! Отправь фото своего мотика, и я переобулю его в мотарды 17/17 с дисками в цвет."
    )

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    sent_msg = bot.reply_to(message, "⏳ Переделываю колеса в мотарды 17/17, жди...")
    
    input_path = f"input_{message.chat.id}.jpg"
    output_path = f"output_{message.chat.id}.jpg"
    
    try:
        # 1. Скачиваем фото от пользователя
        photo_file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(photo_file_info.file_path)
        
        with open(input_path, 'wb') as f:
            f.write(downloaded_file)
            
        # 2. Используем модель instruct-pix2pix для редактирования по фото и промпту
        api_img2img_url = "https://api-inference.huggingface.co/models/timbrooks/instruct-pix2pix"
        
        with open(input_path, "rb") as f:
            response = requests.post(
                api_img2img_url,
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                files={"image": f},
                data={"inputs": CUSTOM_PROMPT}
            )

        # Проверяем успешность ответа (сервер возвращает картинку или ошибку)
        content_type = response.headers.get("content-type", "")
        if response.status_code == 200 and "image" in content_type:
            with open(output_path, "wb") as out:
                out.write(response.content)
                
            with open(output_path, "rb") as photo_to_send:
                bot.send_photo(message.chat.id, photo_to_send, caption="🔥 Готово! Лови мотард.")
                
            os.remove(output_path)
        else:
            # Если модель прогревается (ошибка 503 или JSON с предупреждением)
            bot.edit_message_text(
                "⚠️ Нейросеть на сервере «просыпается» (модель загружается). Попробуй отправить фото еще раз через 20-30 секунд.", 
                message.chat.id, 
                sent_msg.message_id
            )
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка выполнения: {e}")
        
    finally:
        # Гарантированно удаляем входной файл, если он остался
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == "__main__":
    print("Бот с мотард-генерацией запущен...")
    bot.infinity_polling()
