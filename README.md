# Something Mobile Shop — Telegram Mini App

Mobile phone e-commerce store built as a Telegram Mini App (works in a normal browser too).

**Live:** https://pwintsan4238.github.io/something-mobile-shop/

```
index.html   ← the whole web app (single file, no build step)
bot/bot.py   ← Telegram bot that opens the shop and receives orders
```

## Features
- 21 products: Apple, Samsung, Xiaomi, OPPO, vivo, Pixel, Honor, realme, Anker
- Brand, category and price filters, search and sorting
- Product page with color and storage options (price changes with storage), stock status, specs, installment estimate, related items, share
- Wishlist, cart with quantity limits by stock, promo codes (`WELCOME5`, `PHONE10`)
- Delivery zones with free shipping over 1,000,000 Ks
- Checkout: COD, KBZPay, WavePay, AYA Pay, CB Pay, installment
- Order history with one-tap re-order
- Telegram theme colors, MainButton, BackButton, haptics, CloudStorage cart

## Customize
Edit the top of the `<script>` in `index.html`:
- `CONFIG` — admin username, delivery zones, free-shipping limit, promo codes
- `PRODUCTS` — name, price, `was` (old price), stock, colors, storage, specs. Add `img: "https://..."` to use a real photo.
- `SLIDES` — banner carousel

Push to `main` and GitHub Pages updates in about a minute.

## Connect the bot
1. **@BotFather** → `/newbot` → copy the token.
2. Run the bot:
   ```
   pip install python-telegram-bot==21.6
   set BOT_TOKEN=123:abc
   set WEBAPP_URL=https://pwintsan4238.github.io/something-mobile-shop/
   set ADMIN_CHAT_ID=123456789
   python bot/bot.py
   ```
3. Send `/start` to the bot → tap **🛍️ ဆိုင်ကို ဖွင့်မည်**.

> `tg.sendData()` only works when the app is opened from the reply-keyboard button that `/start` shows.
> For the Menu Button or inline buttons, set `CONFIG.ORDER_API` to your own backend and verify `initData` there.
