import os
import asyncio
import logging
from datetime import datetime
from anthropic import Anthropic

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from agents import PriceAgent, SentimentAgent, OrchestratorAgent

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY")

client = Anthropic(api_key=ANTHROPIC_API_KEY)
COINS = ["BTC", "ETH", "BNB", "SOL", "XRP"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("📊 Анализ монеты", callback_data="choose_coin")],
        [InlineKeyboardButton("🌐 Рынок целиком", callback_data="market_overview")],
        [InlineKeyboardButton("😱 Fear & Greed", callback_data="fear_greed")],
        [InlineKeyboardButton("ℹ️ Об агентах", callback_data="about")],
    ]
    await update.message.reply_text(
        "🤖 *Crypto AI Agents Bot*\n\n"
        "Система из 3 агентов на базе Claude:\n"
        "• 📈 *PriceAgent* — цены и тренды\n"
        "• 🧠 *SentimentAgent* — настроения рынка\n"
        "• 🎯 *OrchestratorAgent* — итоговая рекомендация\n\n"
        "Выберите действие:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def choose_coin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton(f"🪙 {c}", callback_data=f"analyze_{c}") for c in COINS[:3]],
        [InlineKeyboardButton(f"🪙 {c}", callback_data=f"analyze_{c}") for c in COINS[3:]],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_main")],
    ]
    await query.edit_message_text(
        "Выберите монету для анализа:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def analyze_coin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    coin = query.data.split("_")[1]
    await query.edit_message_text(f"⏳ Агенты анализируют *{coin}*...", parse_mode="Markdown")
    price_agent = PriceAgent(client)
    sentiment_agent = SentimentAgent(client)
    orchestrator = OrchestratorAgent(client)
    price_data = await price_agent.analyze(coin)
    sentiment_data = await sentiment_agent.analyze(coin)
    final = await orchestrator.synthesize(coin, price_data, sentiment_data)
    text = (
        f"📊 *Анализ {coin}* — {datetime.now().strftime('%H:%M %d.%m.%Y')}\n"
        f"{'─'*35}\n\n"
        f"📈 *PriceAgent*\n{price_data['summary']}\n​​​​​​​​​​​​​​​​
