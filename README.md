# 🎌 بوت الأنمي والأفلام — نسخة Railway (مجانية 24/7)

البوت يعمل على سيرفر مجاني في السحابة، لا يحتاج حاسوب أو هاتف مفتوح!

---

## ✅ ما تحتاجه قبل البدء
- حساب GitHub (مجاني): https://github.com
- حساب Railway (مجاني): https://railway.app
- توكن بوت تيليغرام
- مفتاح Anthropic API

---

## 🚀 خطوات الرفع على Railway

### 1️⃣ احصل على توكن البوت
1. افتح تيليغرام → ابحث عن @BotFather
2. أرسل /newbot واتبع الخطوات
3. انسخ التوكن

### 2️⃣ احصل على مفتاح Anthropic
1. اذهب إلى https://console.anthropic.com
2. سجل حساب مجاني
3. من القائمة: API Keys ← Create Key
4. انسخ المفتاح

### 3️⃣ ارفع الملفات على GitHub
1. اذهب إلى https://github.com وسجل دخول
2. اضغط New repository (الزر الأخضر)
3. سمّه anime-bot واضغط Create repository
4. اضغط "uploading an existing file"
5. ارفع الملفات الأربعة: bot.py و requirements.txt و Procfile و railway.json
6. اضغط Commit changes

### 4️⃣ شغّل على Railway
1. اذهب إلى https://railway.app
2. اضغط Start a New Project
3. اختر Deploy from GitHub repo
4. اختر repo اللي أنشأته anime-bot
5. اضغط Deploy Now

### 5️⃣ أضف المفاتيح السرية
بعد الرفع مباشرة:
1. اضغط على المشروع
2. اذهب إلى تبويب Variables
3. اضغط New Variable وأضف:
   - TELEGRAM_TOKEN = توكن البوت من BotFather
   - ANTHROPIC_API_KEY = مفتاح Anthropic
4. Railway سيعيد تشغيل البوت تلقائياً ✅

---

## 🎮 استخدام البوت
- /start — القائمة الرئيسية
- /help — المساعدة
- /clear — مسح المحادثة
- اكتب مثلاً: "اقترح لي أنمي أكشن"

---

## 📦 الملفات
- bot.py           ← كود البوت
- requirements.txt ← المكتبات
- Procfile         ← يخبر Railway كيف يشغّل البوت
- railway.json     ← إعدادات Railway
- README.md        ← هذا الملف
