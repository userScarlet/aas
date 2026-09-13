import os
import requests
from telebot import TeleBot
from huggingface_hub import InferenceClient

TOKEN = "8998319147:AAEMBPz3apnk8tw2vQEtono9M07Idr8YKvE"
HF_TOKEN = "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" 

bot = TeleBot(TOKEN)
client = InferenceClient(api_key=HF_TOKEN)

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
        # Скачиваем фото от пользователя
        photo_file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(photo_file_info.file_path)
        
        with open(input_path, 'wb') as f:
            f.write(downloaded_file)
            
        # Используем официальный клиент для Instruct-Pix2Pix
        with open(input_path, "rb") as f:
            image_bytes = f.read()
            
        # Запрос через новый шлюз Hugging Face Inference Providers
        image_response = client.image_to_image(
            image=image_bytes,
            prompt=CUSTOM_PROMPT,
            model="timbrooks/instruct-pix2pix"
        )
        
        # Сохраняем результат
        image_response.save(output_path)
                
        with open(output_path, "rb") as photo_to_send:
            bot.send_photo(message.chat.id, photo_to_send, caption="🔥 Готово! Лови мотард.")
            
        os.remove(output_path)
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка выполнения: {e}")
        
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == "__main__":
    print("Бот с мотард-генерацией запущен...")
    bot.infinity_polling()
