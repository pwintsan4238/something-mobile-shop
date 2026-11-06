"""
Something Mobile Shop — Telegram bot that opens the Mini App and receives orders.

pip install python-telegram-bot==21.6
set env vars:  BOT_TOKEN, WEBAPP_URL (https URL of webapp/index.html), ADMIN_CHAT_ID (your chat id)
python bot.py
"""
import json
import os

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, WebAppInfo
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          MessageHandler, filters)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_URL = os.environ["WEBAPP_URL"]
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))


def ks(n: int) -> str:
    return f"{n:,} Ks"


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # tg.sendData() only works when the Mini App is opened from a *reply keyboard* button.
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("🛍️ ဆိုင်ကို ဖွင့်မည်", web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True,
    )
    await update.message.reply_text(
        "မင်္ဂလာပါ 🙏 Something Mobile Shop မှ ကြိုဆိုပါတယ်။\n"
        "အောက်က ခလုတ်ကို နှိပ်ပြီး ပစ္စည်းများ ကြည့်ရှု မှာယူနိုင်ပါတယ်။",
        reply_markup=kb,
    )


async def on_order(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    order = json.loads(update.effective_message.web_app_data.data)
    c = order["customer"]
    lines = "\n".join(
        f"• {i['name']}" + (f" ({i['option']})" if i.get("option") else "")
        + f" × {i['qty']} = {ks(i['price'] * i['qty'])}"
        for i in order["items"]
    )
    discount = (
        f"Promo {order['promo']}: -{ks(order['discount'])}\n" if order.get("discount") else ""
    )
    text = (
        f"🧾 Order #{order['id']}\n\n{lines}\n\n"
        f"ပစ္စည်းတန်ဖိုး: {ks(order['subtotal'])}\n"
        f"{discount}"
        f"ပို့ဆောင်ခ: {ks(order['delivery']) if order['delivery'] else 'အခမဲ့'}\n"
        f"စုစုပေါင်း: {ks(order['total'])}\n"
        f"ငွေပေးချေမှု: {order['payment']}\n\n"
        f"👤 {c['name']}\n📞 {c['phone']}\n📍 {c.get('zone', '')} — {c['address']}"
        + (f"\n📝 {c['note']}" if c.get("note") else "")
    )
    await update.effective_message.reply_text(
        "✅ အော်ဒါ လက်ခံရရှိပါပြီ။ မကြာမီ ဆက်သွယ်ပေးပါမည်။\n\n" + text
    )
    if ADMIN_CHAT_ID:
        u = update.effective_user
        who = f"@{u.username}" if u.username else f"id {u.id}"
        await ctx.bot.send_message(ADMIN_CHAT_ID, f"🔔 New order from {who}\n\n{text}")


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, on_order))
    app.run_polling()


if __name__ == "__main__":
    main()
