import discord
import os
import base64
import pymongo
from groq import Groq
from discord.ext import commands

# --- 1. ตั้งค่า Groq AI ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- 2. ตั้งค่า MongoDB ---
MONGO_URL = os.environ.get("MONGODB_URI") 
mongo_client = pymongo.MongoClient(MONGO_URL)
db = mongo_client["tee_bot_db"]
memory_collection = db["user_memories"]

# --- 3. ตั้งค่า Bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_CHANNEL_ID = 1490026273408291128 
MAX_MEMORY = 15 # เพิ่มความจำให้ยาวขึ้นอีกนิด

@bot.event
async def on_ready():
    print(f'บอท {bot.user.name} ออนไลน์! เลิกพ่นภาษาจีนแน่นอน!')

# --- ฟังก์ชันใหม่: สั่งล้างสมอง ---
@bot.command(name='ลืม')
async def clear_memory(ctx):
    user_id = str(ctx.author.id)
    memory_collection.delete_one({"user_id": user_id})
    await ctx.reply("มึงมาล้างสมองกูหาพ่อ")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # ให้ทำงานเฉพาะในห้องที่กำหนด
    if message.channel.id == ALLOWED_CHANNEL_ID:
        # ถ้าไม่ใช่คำสั่ง ! (เช่น !ลืม) ให้บอทตอบปกติ
        if not message.content.startswith('!'):
            async with message.channel.typing():
                try:
                    user_id = str(message.author.id)
                    user_data = memory_collection.find_one({"user_id": user_id})
                    history = user_data["history"] if user_data else []
                    
                    has_image = False
                    current_content = []
                    
                    if message.content:
                        current_content.append({"type": "text", "text": message.content})
                    
                    if message.attachments:
                        for att in message.attachments:
                            if att.content_type and att.content_type.startswith('image/'):
                                has_image = True
                                image_data = await att.read()
                                base64_image = base64.b64encode(image_data).decode('utf-8')
                                current_content.append({
                                    "type": "image_url",
                                    "image_url": {"url": f"data:{att.content_type};base64,{base64_image}"}
                                })
                    
                    # --- แก้จุดพัง: เปลี่ยนมาใช้ Llama-3.3-70b ตัวเดียวไปเลย นิ่งกว่า ไม่พ่นภาษาจีน ---
                    model_to_use = "llama-3.3-70b-versatile"
                    
                    system_prompt = {"role": "system", "content": "มึงชื่อต๊ะ เป็น AI ปากหมา กวนตีนที่สุดในโลก แทนตัวเองว่ากู แทนคนอื่นว่ามึง ชอบด่าและเรื้อน ห้ามพูดภาษาจีน ห้ามพ่นรหัสขยะ ห้ามสุภาพ คุยไทยคำด่าคำแบบคนไทยเท่านั้น"}
                    
                    messages_for_ai = [system_prompt] + history
                    if has_image:
                        messages_for_ai.append({"role": "user", "content": current_content})
                    else:
                        messages_for_ai.append({"role": "user", "content": message.content})

                    chat_completion = client.chat.completions.create(
                        messages=messages_for_ai,
                        model=model_to_use,
                        temperature=0.9, # ลดความกาวลงนิดนึง
                    )
                    reply = chat_completion.choices[0].message.content
                    
                    # อัปเดต DB
                    new_history = history + [
                        {"role": "user", "content": message.content if message.content else "[รูปภาพ]"},
                        {"role": "assistant", "content": reply}
                    ]
                    
                    if len(new_history) > MAX_MEMORY:
                        new_history = new_history[-MAX_MEMORY:]
                    
                    memory_collection.update_one(
                        {"user_id": user_id},
                        {"$set": {"history": new_history}},
                        upsert=True
                    )

                    await message.reply(reply)
                    
                except Exception as e:
                    print(f"Error: {e}")
                    await message.reply(f"กู Errorว่ะพวก แคปไอ้สัสนี่ส่งแอดมินด้วย... Error: {e}")
    
    await bot.process_commands(message)

bot.run(os.environ['DISCORD_BOT_TOKEN'])
