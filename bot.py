import logging
import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PyPDF2 import PdfReader, PdfWriter

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

menu = ReplyKeyboardMarkup(
    [
        ["📄 Compress PDF"],
        ["ℹ️ About Bot", "🛠 Help"],
        ["👨‍💻 Developer"]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Cloud PDF Compressor Bot!\n\n"
        "This bot helps users upload PDF files and receive an optimized version.\n\n"
        "Please choose one option from the menu below:",
        reply_markup=menu
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📄 Compress PDF":
        await update.message.reply_text(
            "📤 Please send your PDF file.\n\n"
            "After receiving it, I will process and return the compressed version."
        )

    elif text == "ℹ️ About Bot":
        await update.message.reply_text(
            "ℹ️ About This Bot\n\n"
            "Cloud PDF Compressor Bot is a simple cloud-based Telegram bot.\n"
            "It receives PDF files from users, processes them, and sends back an optimized PDF file.\n\n"
            "This project was created for the Cloud Technologies assignment."
        )

    elif text == "🛠 Help":
        await update.message.reply_text(
            "🛠 How to use this bot:\n\n"
            "1. Click 📄 Compress PDF\n"
            "2. Send a PDF file\n"
            "3. Wait for processing\n"
            "4. Download the returned PDF file\n\n"
            "Note: Only PDF files are supported."
        )

    elif text == "👨‍💻 Developer":
        await update.message.reply_text(
            "👨‍💻 Developer Information\n\n"
            "Created by: Abdusamatov Suxrob\n"
            "Project: Cloud PDF Compressor Bot\n"
            "Platform: Telegram + Render.com\n"
            "Language: Python"
        )

    else:
        await update.message.reply_text(
            "Please choose an option from the menu below.",
            reply_markup=menu
        )

async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document

    if file.mime_type != "application/pdf":
        await update.message.reply_text("❌ Please send only a PDF file.")
        return

    await update.message.reply_text("✅ PDF received.\n⏳ Processing your file...")

    file_obj = await file.get_file()
    input_path = "input.pdf"
    output_path = "compressed.pdf"

    await file_obj.download_to_drive(input_path)

    original_size = os.path.getsize(input_path)

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    compressed_size = os.path.getsize(output_path)
    pages = len(reader.pages)

    await update.message.reply_text(
        f"✅ Processing completed!\n\n"
        f"📄 Pages: {pages}\n"
        f"📦 Original size: {round(original_size / 1024, 2)} KB\n"
        f"📉 Optimized size: {round(compressed_size / 1024, 2)} KB\n\n"
        f"Here is your processed PDF:"
    )

    with open(output_path, "rb") as pdf_file:
        await update.message.reply_document(document=pdf_file)

    os.remove(input_path)
    os.remove(output_path)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_pdf))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot is running...")
    app.run_polling()
