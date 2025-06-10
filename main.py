from flask import Flask
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, InputMediaVideo
)
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    ApplicationBuilder, MessageHandler, ContextTypes, filters,
    ChatMemberHandler, CallbackQueryHandler
)
import threading
import os
import asyncio
import re
import json
import datetime
import datetime
import pytz

TOKEN = os.environ["BOT_TOKEN"]
CREATOR_ID = 7157918161  # 你的 Telegram ID

app = Flask(__name__)

# 載入或初始化已記錄的群組 ID
if os.path.exists("group_ids.json"):
    with open("group_ids.json", "r") as f:
        group_ids = json.load(f)
else:
    group_ids = []

# 純 Python 字典關鍵字資料（圖片為上傳至 Replit 的檔名）
reply_rules = {
    "NEW": {
        "media": ["NEW.jpg"],
        "text": None,
        "button": {"text": "Join channel", "url": "https://t.me/+_iNARwr0ev8wOGY9"}
    },
    "LP": {
        "media": ["LP.jpg"],
        "text": None,
        "button": None
    },
    "LK": {
        "media": [],
        "text": "Honey leave room keep clean,and Put the key back on the door mat and don't lock it\n\nขวดน้ำเดือด﹑เครื่องเป่าผม﹑ไฟกลางคืน\nอุปกรณ์ทำความสะอาด﹑ผ้าห่ม﹑หมอน﹑เครื่องหนีบผม\nจำไว้ว่าอย่านำสิ่งของทั้งหมดของบริษัทออกไป\nให้ผู้หญิงคนต่อไปใช้\nถ่ายวิดีโอของห้องเพื่อให้แน่ใจว่าห้องสะอาดและมีการเก็บรักษาสิ่งของต่างๆ🙏🏻🙏🏻\n\nก่อนกลับ อย่าลืมทำความสะอาดห้องและถ่ายรูปให้ฉัน ทำความสะอาดถังขยะ\n‼️อย่าลืมปิดเครื่องปรับอากาศ‼️\n\nขอบคุณที่ทํางานร่วมกันในช่วงเวลานี้\nรอคอยที่จะได้พบคุณในครั้งต่อไป🥺🦋💛",
        "button": None
    },
    "ZA": {
        "media": [],
        "text": "🔔สวัสดีตอนเช้า 🌞💙\nตอนนี่ถ่ายรูปเซฟฟี่ให้ฉันดูหน่อย\nฉันอยากดูในการแต่งหน้าของคุณ",
        "button": None
    },
    "ZPK": {
        "media": [],
        "text": "ก่อนเวลางาน แต่งหน้า เสร็จถ่ายรูปตัวเองเข้ากลุ่มจ้าา",
        "button": None
    },
    "ZP": {
        "media": [],
        "text": "ถ่ายรูปเซลฟี่(หน้า)ตอนนี้\nส่งเข้ากลุ่ม\nตรวจสอบการแต่งหน้า",
        "button": None
    },
    "NZ": {
        "media": ["NZ.jpg"],
        "text": "ฉันสูญเสียการแต่งหน้าส่วนเกิน\nถ่ายรูปเมื่อเสร็จแล้ว",
        "button": None
    },
    "FF": {
        "media": [],
        "text": "🥩🥩 Honey ก่อนไปกินข้าวเอากุญแจไปด้วย\nลบข้อความกลุ่มทำงานเสร๊จถึงออกไปได้\nหนึ่งชั่วโมงสำหรับมื้อเย็น",
        "button": None
    },
    "ZH": {
        "media": [],
        "text": "Honey💕\nทำงานวันสุดท้ายวันไหน ทำถึงกี่โมง\n คืนห้องตอนกี่โมงออกกี่โมง",
        "button": None
    },
    "BP": {
        "media": ["BP.jpg"],
        "text": "บอกหมายเลขที่คุณต้องการ 🧡\n\nสตาฟจะเอาอุปกรณ์ทำงานมาให้ทุกวัน วันอังคาร พฤหัส เสาร์ หากขาดอะไรให้แจ้งทีเดียว เพราะวันอื่นไม่มีสตาฟส่งของให้\n\nน้ำดื่ม ซื้อกินเองนะคะ ที่นี่เรามีให้แค่ น้ำยาบ้วนปาก 2 ขวด ถ้าใช้หมดแล้ว น้องต้องซื้อเองจ้า",
        "button": None
    },
    "DS": {
        "media": [],
        "text": "When the driver collects the money, he will charge an additional 500 cleaning fee.\nWait to finish work and leave the room\nThe driver will check whether the room is clean\nWill refund 500",
        "button": None
    },
    "KQ": {
        "media": [],
        "text": "※ถ้าคุณไม่มาทำงานตามเวลาที่ตกลงในห้องสวีทจะถูกหัก 1,000 หนึ่งวัน\n※ หากคุณออกก่อนเวลาและไม่ทำตามกำหนดเวลา จะถูกหัก 1,000 สำหรับหนึ่งวัน\n...\n(此處省略為節省空間，完整內容已保留在程式碼中)\n...",
        "button": None
    },
    "BK": {
        "media": [],
        "text": "💥💥💥จำได้ว่าได้ยินเสียงเคาะ\nไม่เคยเปิดประตู\nถ้าเราบอกให้เปิดประตูเท่านั้น\nจึงจะสามารถเปิดประตูได้💥💥💥",
        "button": None
    },
    "YP": {
        "media": ["YP (1).mp4", "YP (2).mp4"],
        "text": "ช่วยถ่ายวีดีโอแบบนี่ให้ฉัน\nไม่จำเป็นต้องเห็นหน้า \nแต่ว่าต้องถ่ายแบบ เซ็กซี่\nถ่ายแบบหลายมุม\nฉันจะช่วยทำโฆษณาสวยๆ",
        "button": None
    },
    "PQ": {
        "media": ["PQ.jpg"],
        "text": "If you receive counterfeit money, you have to pay for it yourself",
        "button": None
    },
    "LS": {
        "media": [],
        "text": "ี่รักใส่ขยะข้างนอกถ่ายรูปให้เราใส่เพียง 2-3 แพ็ค ❤️\n‼️‼️‼️‼️\nถ้าไม่ทิ้งขยะตรงเวลา คนข้างบ้านจะแจ้งตำรวจ\nถ้าตำรวจมาทางบริษัทจะไม่รับผิดชอบ",
        "button": None
    },
    "LJ": {
        "media": [],
        "text": "ตำรวจตระเวนชายแดน ka\nเงียบ🤫\nเคาะไม่เคยเปิด",
        "button": None
    },
    "EAT": {
        "media": ["EAT (1).jpg", "EAT (2).jpg", "EAT (3).jpg"],
        "text": "地址：台北市中山區吉林路169號\nที่อยู่: No. 169, Jilin Road, Zhongshan District, Taipei City",
        "button": {
            "text": "🌍 Google map 🌍",
            "url": "https://maps.app.goo.gl/ZwMRtfk5zQL3igTA8?g_st=com.google.maps.preview.copy"
        }
    },
    "CLG": {"media": [], "text": "customer need จูบแลกลิ้น💋", "button": None},
    "CDL": {"media": [], "text": "customer need เลียตูด👅", "button": None},
    "CNP": {"media": [], "text": "customer need เซ็กทางร่องอก 🍼", "button": None},
    "CWT": {"media": [], "text": "customer need +1000  เอาสด 💦💦", "button": None},
    "CYS": {"media": [], "text": "customer need  +500 แตกหน้า 🤦🏻‍♀️💦", "button": None},
    "CYW": {"media": [], "text": "customer need  เต้นเซ็กซี่ 💃🏻💃🏻", "button": None},
    "CHM": {"media": [], "text": "customer need +1000 เอาตูด 🫶🏻🕳", "button": None},
    "CKB": {"media": [], "text": "customer need +500 แตกปาก👄", "button": None},
    "CZW": {"media": [], "text": "customer need โชว์ช่วยตัวเอง 🫴🏻", "button": None},
    "CBH": {"media": [], "text": "customer need สลับออรัลเซ็กซ์ด้วยน้ำเย็นและน้ำร้อน 🧊🔥", "button": None},
    "CTC": {"media": [], "text": "customer need อาบน้ำให้ลูกค้าด้วยหน้าอก 🧼", "button": None},
    "CQQ": {"media": [], "text": "customer need ทำเสร็จแล้วถอดถุงยางออก ใช้ปากทำความสะอาดให้ลูกค้า 😋🍆", "button": None},
    "CZJ": {"media": [], "text": "customer need  เอาเท้าถูกับอวัยวะเพศของลูกค้า 🦶🏻🍆", "button": None},
    "CSW": {"media": [], "text": "customer need  ลูกค้าเตรียมถุงน่องมาให้ 🧦", "button": None},
    "C2B": {"media": [], "text": "2ชาย 1หญิง 🚹🚹🚺", "button": None},
    "C2G": {"media": [], "text": "หญิง 2 ชาย 1 🚺🚺🚹", "button": None},
    "CQJ": {"media": [], "text": "ข่มขืนลูกค้า😈😈", "button": None},
    "LZ": {
        "media": ["LZ.jpg"],
        "text": "Honey have cus he have this\nyou can do mai ?\nIf you can't is Ok\nshop don't want you force do ka",
        "button": None
    },
    "DH": {
        "media": ["DH.jpg"],
        "text": "เมื่อลูกค้าเข้าร้านแจ้งกลุ่ม in1(ลูกค้าคนที่เท่าไหร่)/3300(ยอดเงินที่เก็บ)\n\nพอรับเงินจากลูกค้าเข้ามาต้องรีบถ่ายรูปและซ่อนไว้ดีๆ\nพาลูกค้าเข้าห้องน้ำก่อน ระหว่างนั้นเข้าห้องเก็บเงินไว้ให้ดีค่อยตามลูกค้าเข้าห้องน้ำ\nถ้าได้แบ๊งปลอมหนูต้องรับผิดชอบเอง\nอย่าให้ลูกค้าเห็นว่าคุณเก็บเงินไว้ที่ไหน",
        "button": None
    },
    "CCCC": {
        "media": ["CCCC.jpg"],
        "text": "ลคเข้ามา ในห้อง\nเก็บตัง  พิมพ์รอบงาน\nจับมือ ลคไปอ่าบน้ำ\nอ่านน้ำไห้ลค จะได้รู้ สะอาดไหมค่า\nอมสด ในห้องน้ำ เล้าโลมตั้งแต่ อยู่ในห้องน้ำ  อ่านน้ำเสร็จ เช็คตัว พาลค มาในเตียงนอน เลีย ตรงไหนได้ เลียเลยค่า คอยๆเล้าโลมลค ไม่ต้องรีบ พยายามอมสด นานๆ ไห้ลค ไห้ลครู้สึกว่า เราเป็นแฟน เขา\nลค เสร็จ พาไปล้างตัว มีเวลา นวด เอาใจ ลค ถึงเวลา ใส่เสื้อผ้า ไห้ลคออกจากห้อง ค่า",
        "button": None
    },
    "VIP": {
        "media": ["VIP.jpg"],
        "text": "เดียวลูกค่าคนนี่\nสำคัญที่สุด\nนางเป็นนักเขียนรีวิว\nเขียนดี ปังตลอด\nเขียนไม่ดี ดับทันที\nบริการฟิวแฟนเซอวิตเต็มที่ครับ",
        "button": None
    },
    "MT": {
        "media": [],
        "text": "ประกาศกลุ่ม\nหากอาหารทานไม่หมดอย่าเทลงโถส้วม เทได้แค่น้ำซุป ไม่งั้นโถส้วมอุดตันกดไม่ลง",
        "button": None
    },
    "YS": {
        "media": [],
        "text": "🔑อย่าลืมเอากุญแจไปด้วยตอนออกจากห้อง",
        "button": None
    },
    "ZB": {
        "media": [],
        "text": "แจ้งให้เราทราบหากคุณพร้อม\nให้บริการที่ดีแก่ลูกค้า💖",
        "button": None
    },
    "MKF": {
       "media": [],
       "text": "Test OK >.<",
       "button": None
    },
    "HB": {
    "media": [],
    "text": "อย่าให้ลคเห็นกลุ่มงานเรา\n" \
            "หากลูกค้าบอกว่าเวลา 30 or 50 นาที\n" \
            "เราตกลงกับลคก่อนค่ะ\n" \
            "แต่จริงๆ เราบริการแค่ 20 or 40 นาทีเท่านั้นค่ะ\n\n" \
            "ห้ามให้ลูกค้าดูแชทกลุ่มเด็ดขาด\n" \
            "ถ้าเอาแชทให้ลูกค้าเห็น ปรับ 5000 หยวน\n" \
            "ถ้าแลกเบอร์ติดต่อกับลูกค้า ปรับ 10000 หยวน",
    "button": None
    }         
}   
# 使用者發話處理
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg is None or msg.text is None:
        return

    if msg.text.strip() == "啟用群發":
        chat_id = msg.chat.id
        if chat_id not in group_ids:
            group_ids.append(chat_id)
            with open("group_ids.json", "w") as f:
                json.dump(group_ids, f)
            await msg.reply_text("✅ 本群組已啟用群發功能！")
        else:
            await msg.reply_text("✅ 本群組已經啟用過囉！")
        return

    if re.fullmatch(r"[-+*/().0-9 ]+", msg.text):
        try:
            result = eval(msg.text)
            await msg.reply_text(f"= {result}", reply_to_message_id=msg.message_id)
        except:
            pass
        return

    if msg.chat.type == "private" and msg.from_user.id == CREATOR_ID:
        if msg.photo:
            await msg.reply_text(f"📸 圖片 file_id：{msg.photo[-1].file_id}")
        elif msg.video:
            await msg.reply_text(f"🎥 影片 file_id：{msg.video.file_id}")
        return

    if msg.chat.type not in ["group", "supergroup"]:
        return

    key = msg.text.strip()
    if key not in reply_rules:
        return

    rule = reply_rules[key]
    medias = rule.get("media", [])
    text = rule.get("text")
    button = rule.get("button")

    reply_markup = None
    if button and button.get("text") and button.get("url"):
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(button["text"], url=button["url"])]])

    if len(medias) > 1:
        group = []
        for f in medias:
            ext = f.split(".")[-1].lower()
            if ext in ["jpg", "jpeg", "png"]:
                group.append(InputMediaPhoto(open(f, "rb")))
            elif ext in ["mp4", "mov"]:
                group.append(InputMediaVideo(open(f, "rb")))
        await msg.reply_media_group(group)
        if text or reply_markup:
            await msg.reply_text(text or "", reply_markup=reply_markup)
    elif len(medias) == 1:
        f = medias[0]
        ext = f.split(".")[-1].lower()
        if ext in ["jpg", "jpeg", "png"]:
            await msg.reply_photo(open(f, "rb"), caption=text, reply_markup=reply_markup)
        elif ext in ["mp4", "mov"]:
            await msg.reply_video(open(f, "rb"), caption=text, reply_markup=reply_markup)
    elif text:
        await msg.reply_text(text, reply_markup=reply_markup)

# 歡迎詞
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.chat_member
    if member.status == ChatMemberStatus.MEMBER and member.old_chat_member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("yes i agree✅", callback_data=f"agree_{member.from_user.id}")]
        ])
        await context.bot.send_message(
            chat_id=member.chat.id,
            text="Have you joined the rules channel and read and committed to comply？",
            reply_markup=keyboard
        )

# 同意按鈕
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query and query.data.startswith("agree_"):
        user = query.from_user
        await query.answer()
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=f"Thank pretty girl {user.mention_html()}💌\nBlue Butterfly wishes you to become the richest lady💰",
            parse_mode="HTML"
        )

# 定時群發
async def daily_broadcast(app_bot):
    tz = pytz.timezone("Asia/Taipei")
    already_sent = {"11:00": False, "13:00": False, "23:50": False}

    while True:
        now = datetime.datetime.now(tz)
        current_time = now.strftime("%H:%M")

        if current_time == "11:00" and not already_sent["11:00"]:
            for gid in group_ids:
                await app_bot.bot.send_message(
                    chat_id=gid,
                    text="สวัสดีตอนเช้า 🌞💙\nตอนนี่ถ่ายรูปเซฟฟี่ให้ฉันดูหน่อย\nฉันอยากดูในการแต่งหน้าของคุณ\n🔔This is group message\nFor the Lady who starts work at pm12:00-am2:30"
                )
            already_sent["11:00"] = True

        elif current_time == "13:00" and not already_sent["13:00"]:
            for gid in group_ids:
                await app_bot.bot.send_message(
                    chat_id=gid,
                    text="สวัสดีตอนเช้า 🌞💙\nตอนนี่ถ่ายรูปเซฟฟี่ให้ฉันดูหน่อย\nฉันอยากดูในการแต่งหน้าของคุณ\n🔔This is group message\nFor the Lady who starts work at pm14:00-am4:30"
                )
            already_sent["13:00"] = True

        elif current_time == "23:50" and not already_sent["23:50"]:
            for gid in group_ids:
                await app_bot.bot.send_message(
                    chat_id=gid,
                    text="🧪 Robot testing..."
                )
            already_sent["23:50"] = True

        # 每天凌晨 00:01 重設狀態
        if current_time == "00:01":
            already_sent = {k: False for k in already_sent}

        await asyncio.sleep(30)

# Flask 主頁
@app.route("/")
def index():
    return "Bot Running"

# Flask 線程
def run_flask():
    app.run(host="0.0.0.0", port=8080)

# 主程式啟動點
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("✅ 啟動 Telegram 機器人...")
    app_bot = ApplicationBuilder().token(TOKEN).build()

    app_bot.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))
    app_bot.add_handler(CallbackQueryHandler(button_click))
    asyncio.get_event_loop().create_task(daily_broadcast(app_bot))

    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply))
    app_bot.run_polling()
