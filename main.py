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
ALLOWED_CHANNEL_ID = 14900026273408291128

@bot.event
async def on_ready():
    # ลบ keep_alive ออกไปแล้ว
    print(f'บอทสายคุย {bot.user.name} ตื่นแล้ว! (รันบน GitHub Actions ไม่หลับ 100%)')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == ALLOWED_CHANNEL_ID:
        if not message.content.startswith('!'):
            async with message.channel.typing():
                try:
                    # สั่งให้ออกลุยแบบกวนๆ
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "ตอบคำถามหรือคุยกับผู้คนแบบกวนๆในภาษาไทย กวนตีนและชอบด่าและแน่นอนมึงเรื้อนและกาม"}, # มึงแก้ prompt ตรงนี้ได้นะถ้าอยากให้มันนิสัยเปลี่ยน
                            {"role": "user", "content": message.content}
                        ],
                        model="llama-3.3-70b-versatile",
                    )
                    reply = chat_completion.choices[0].message.content
                    await message.reply(reply)
                except Exception as e:
                    print(f"Error: {e}")
                    await message.reply("สมองลัดวงจรว่ะ มึงลองใหม่ดิ")
    
    await bot.process_commands(message)

# รันบอท (ใช้ชื่อ Secret ให้ตรงกับใน GitHub)
bot.run(os.environ['DISCORD_BOT_TOKEN'])
