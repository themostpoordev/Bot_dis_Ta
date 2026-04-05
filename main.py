import discord
import os
import base64
from groq import Groq
from discord.ext import commands

# --- ตั้งค่า Groq AI ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- ตั้งค่า Bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# !!! อย่าลืมเช็คเลข ID ห้องให้ตรงนะ !!!
ALLOWED_CHANNEL_ID = 1490026273408291128

@bot.event
async def on_ready():
    print(f'บอทสายคุย {bot.user.name} ตื่นแล้ว! พร้อมส่องรูปด้วยระบบ Base64 ทะลวงไส้!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == ALLOWED_CHANNEL_ID:
        if not message.content.startswith('!'):
            async with message.channel.typing():
                try:
                    user_message_content = []
                    has_image = False
                    
                    if message.content:
                        user_message_content.append({"type": "text", "text": message.content})
                    elif message.attachments:
                        user_message_content.append({"type": "text", "text": "ดูรูปนี้แล้ววิจารณ์หน่อย กวนตีนๆเลยนะ"})

                    if message.attachments:
                        for att in message.attachments:
                            # เช็คว่าเป็นไฟล์รูป
                            if att.content_type and att.content_type.startswith('image/'):
                                has_image = True
                                
                                # --- จุดที่อัปเกรด: โหลดรูปแล้วแปลงเป็นรหัส Base64 ---
                                image_data = await att.read() # ให้บอทโหลดรูปมาเก็บไว้
                                base64_image = base64.b64encode(image_data).decode('utf-8') # แปลงเป็นรหัส
                                mime_type = att.content_type
                                
                                # ยัดรหัสรูปลงไปตรงๆ ไม่ง้อลิงก์!
                                user_message_content.append({
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}
                                })

                    model_to_use = "llama-3.2-90b-vision-preview" if has_image else "llama-3.3-70b-versatile"
                    final_content = user_message_content if has_image else message.content

                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "ตอบคำถามหรือคุยกับผู้คนแบบกวนๆในภาษาไทย ชื่อต๊ะ แทนคนอื่นว่ามึง แทนตัวเองว่ากู กวนตีน ชอบด่ามากๆปากหมาสุดๆ เรื้อนและกาม"},
                            {"role": "user", "content": final_content}
                        ],
                        model=model_to_use,
                    )
                    reply = chat_completion.choices[0].message.content
                    await message.reply(reply)
                    
                                except Exception as e:
                    print(f"Error: {e}")
                    await message.reply(f"พังว่ะเพื่อน! เซิร์ฟเวอร์มันบ่นมางี้:\n```\n{e}\n```")

    await bot.process_commands(message)

# รันบอท
bot.run(os.environ['DISCORD_BOT_TOKEN'])
