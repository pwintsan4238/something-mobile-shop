# Something Mobile Shop — Telegram Mini App

Mobile phone e-commerce store built as a Telegram Mini App (works in a normal browser too).

**Live:** https://pwintsan4238.github.io/something-mobile-shop/

```
index.html               ← the web app (no build step)
products.js              ← product list, generated from the Excel price list
tools/import_prices.py   ← Excel → products.js importer
bot/bot.py               ← Telegram bot that opens the shop and receives orders
```

## Update prices from Excel
1. Edit the price list (sheet **All Price List**: Category/Brand, Warranty/Type, Model, RAM/ROM, Colors, Retail price, Stock Status).
2. Run:
   ```
   pip install openpyxl
   python tools/import_prices.py "D:\Downloads\Top_Star_Mobile_Price_List_With_Search_Nov2026.xlsx"
   ```
3. Commit and push `products.js`. The site updates in about a minute.

Only the **retail** price is exported. Wholesale prices and margins never leave your computer —
don't commit the .xlsx file (it is in `.gitignore`).
Rows with the same brand + model become one product with RAM/ROM options. `Few Stock` shows as "FEW STOCK";
write `Out of Stock` in the Stock Status column to stop sales of that option.

## Features
- 38 models / 55 price options from the Top Star Mobile price list (Xiaomi/Redmi, Samsung, Honor, Nubia, M Horse, Thai Global)
- Filters: brand, CEIR Paid / Official 1-year warranty / Thai Global, tablets, price range; search by model, brand or RAM/ROM (e.g. `Note 17`, `A17`, `8+256`)
- Product page with RAM/ROM options (each with its own price), colors available for that option, stock status, installment estimate, other models from the same brand, share
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
