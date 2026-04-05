import discord
import os
from groq import Groq
from discord.ext import commands

# --- ตั้งค่า Groq AI ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- ตั้งค่า Bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# !!! อย่าลืมเปลี่ยนเลข ID ห้องตรงนี้ !!!
ALLOWED_CHANNEL_ID = 1490026273408291128

@bot.event
async def on_ready():
    print(f'บอทสายคุย {bot.user.name} ตื่นแล้ว! พร้อมส่องรูป! (รันบน GitHub Actions)')

@bot.event
async def on_message(message):
    # ป้องกันไม่ให้บอทคุยกับตัวเอง
    if message.author == bot.user:
        return

    if message.channel.id == ALLOWED_CHANNEL_ID:
        if not message.content.startswith('!'):
            async with message.channel.typing():
                try:
                    # 1. เช็คว่ามีรูปภาพแนบมาด้วยไหม
                    user_message_content = []
                    has_image = False
                    
                    # เก็บข้อความที่พิมพ์มาด้วย (ถ้ามี)
                    if message.content:
                        user_message_content.append({"type": "text", "text": message.content})
                    elif message.attachments:
                        # ถ้าส่งรูปมาเพียวๆ ไม่พิมพ์อะไรเลย ให้บอทมันแซะหน่อย
                        user_message_content.append({"type": "text", "text": "ดูรูปนี้แล้ววิจารณ์หน่อย"})

                    # 2. ดึง URL ของรูปภาพส่งไปให้ AI ดู
                    if message.attachments:
                        for att in message.attachments:
                            # กรองเอาเฉพาะไฟล์รูปภาพ
                            if att.content_type and att.content_type.startswith('image/'):
                                has_image = True
                                user_message_content.append({
                                    "type": "image_url",
                                    "image_url": {"url": att.url}
                                })

                    # 3. สลับสมอง: ถ้ารูปมาใช้ Vision, ถ้าข้อความมาใช้ Text ปกติ
                    model_to_use = "llama-3.2-90b-vision-preview" if has_image else "llama-3.3-70b-versatile"
                    
                    # จัดรูปแบบคำถามให้เข้ากับระบบ
                    final_content = user_message_content if has_image else message.content

                    # 4. สั่งให้ออกลุยแบบกวนๆ
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
                    await message.reply("สมองลัดวงจรว่ะ! สงสัยรูปมึงจะอุบาทว์เกินกูรับไหว ลองใหม่ดิ๊")
    
    await bot.process_commands(message)
