# 回傳圖片檔 file_id 給創建者使用
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
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(button["text"], url=button["url"])]] )

    if len(medias) > 1:
        group = []
        for f in medias:
            ext = f.split(".")[-1].lower()
            if ext in ["jpg", "jpeg", "png"]:
                group.append(InputMediaPhoto(open(f"{f}", "rb")))
            elif ext in ["mp4", "mov"]:
                group.append(InputMediaVideo(open(f"{f}", "rb")))
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

@app.route("/")
def index():
    return "Bot Running"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

if name == "main":
    threading.Thread(target=run_flask).start()
    print("✅ 啟動 Telegram 機器人...")
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply))
    app_bot.run_polling()
