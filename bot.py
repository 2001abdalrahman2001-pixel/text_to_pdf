import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black, blue, red, green, white, HexColor
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد السجلات (Logging) لمراقبة أداء البوت
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- الإعدادات الأساسية ---
TOKEN = os.getenv("BOT_TOKEN")  # سيتم جلبه من إعدادات الموقع الذي ستستضيف عليه
FONT_PATH = "arial.ttf"

# تسجيل الخط العربي
try:
    if os.path.exists(FONT_PATH):
        pdfmetrics.registerFont(TTFont('ArabicFont', FONT_PATH))
        ARABIC_FONT_AVAILABLE = True
    else:
        print("⚠️ تنبيه: ملف arial.ttf غير موجود. سيتم استخدام الخط الافتراضي.")
        ARABIC_FONT_AVAILABLE = False
except Exception as e:
    print(f"⚠️ خطأ في تحميل الخط: {e}")
    ARABIC_FONT_AVAILABLE = False

def fix_arabic(text):
    if not ARABIC_FONT_AVAILABLE: return text
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

# --- الدوال الأساسية للبوت ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"مرحباً {user.mention_html()}! 👋"
        "\n\nأنا بوت تحويل النصوص إلى ملفات PDF تدعم العربية."
        "\nأرسل لي أي نص الآن، أو استخدم الأوامر لتعديل الإعدادات."
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    file_name = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # إنشاء ملف PDF
    c = canvas.Canvas(file_name)
    if ARABIC_FONT_AVAILABLE:
        c.setFont('ArabicFont', 14)
    
    # معالجة النص العربي
    processed_text = fix_arabic(text)
    
    # كتابة النص (تبسيط للعملية)
    c.drawString(100, 750, processed_text)
    c.save()

    # إرسال الملف للمستخدم
    with open(file_name, 'rb') as pdf:
        await update.message.reply_document(document=pdf, filename="your_file.pdf")
    
    # حذف الملف من الخادم بعد الإرسال لتوفير المساحة
    if os.path.exists(file_name):
        os.remove(file_name)

# --- تشغيل البوت ---
def main():
    if not TOKEN:
        print("❌ خطأ: لم يتم العثور على BOT_TOKEN في متغيرات البيئة!")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🚀 البوت يعمل الآن...")
    application.run_polling()

if __name__ == '__main__':
    main()
