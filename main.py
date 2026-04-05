import discord
import os
from groq import Groq
from discord.ext import commands
from threading import Thread

# --- ตั้งค่า Groq AI ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- ระบบกันหลับ (UptimeRobot) ---
app = Flask('')
@app.route('/')
def home(): return "Groq AI Bot is online!"
def run(): app.run(host='0.0.0.0', port=8000)
def keep_alive(): Thread(target=run).start()

# --- ตั้งค่า Bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# !!! อย่าลืมเปลี่ยนเลข ID ห้องตรงนี้ !!!
ALLOWED_CHANNEL_ID = 1490026273408291128

@bot.event
async def on_ready():
    print(f'บอทสายคุย {bot.user.name} ตื่นแล้ว! (ใช้ Groq ฟรี 100%)')
    keep_alive()

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    if message.channel.id == ALLOWED_CHANNEL_ID:
        if not message.content.startswith('!'):
            async with message.channel.typing():
                try:
                    # สั่งให้บอทคุยแบบกวนๆ
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "ตอบคำถามเป็นภาษาไทยแบบวัยรุ่น กวนตีนสุดๆ ใช้มึงกู และที่สำคัญ ชอบด่าและเรื้อนมาก กาม"},
                            {"role": "user", "content": message.content},
                        ],
                        model="llama-3.3-70b-versatile", # ตัวนี้ฉลาดมาก
                    )
                    reply = chat_completion.choices[0].message.content
                    await message.reply(reply)
                except Exception as e:
                    print(f"Error: {e}")
                    await message.reply("สมองลัดวงจรว่ะ มึงลองใหม่ดิ")

    await bot.process_commands(message)

bot.run(os.environ['DISCORD_TOKEN'])
