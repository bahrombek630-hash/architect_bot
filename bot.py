import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import (
    Message, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "9257258356:AAH6aoZiLR4Of62FhkrNA0VJAFP9VmjPAIg" 
ADMIN_USERNAME = "@komiljonovv_8"

dp = Dispatcher(storage=MemoryStorage())

# Foydalanuvchilarning taklif qilgan odamlari soni: {user_id: count}
referrals_db = {}

class OrderForm(StatesGroup):
    lang = State()
    project_type = State()
    area = State()
    phone = State()

class CalcForm(StatesGroup):
    calc_type = State()
    calc_area = State()

def lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="O'zbekcha", callback_data="lang_uz"),
         InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
         InlineKeyboardButton(text="English", callback_data="lang_en")]
    ])

def main_menu(lang="uz"):
    if lang == "ru":
        kb = [
            [KeyboardButton(text="Portfel"), KeyboardButton(text="Zakaz qilish")],
            [KeyboardButton(text="🧮 Калькулятор"), KeyboardButton(text="🎁 Рефералы")],
            [KeyboardButton(text="Savollar"), KeyboardButton(text="Aloqa")]
        ]
    elif lang == "en":
        kb = [
            [KeyboardButton(text="Portfolio"), KeyboardButton(text="Order Project")],
            [KeyboardButton(text="🧮 Calculator"), KeyboardButton(text="🎁 Referrals")],
            [KeyboardButton(text="FAQ"), KeyboardButton(text="Contact")]
        ]
    else:
        kb = [
            [KeyboardButton(text="Portfolio"), KeyboardButton(text="Buyurtma berish")],
            [KeyboardButton(text="🧮 Narxni hisoblash"), KeyboardButton(text="🎁 Referallarim")],
            [KeyboardButton(text="Savollar"), KeyboardButton(text="Bog'lanish")]
        ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(CommandStart())
async def command_start_handler(message: Message, command: CommandObject, state: FSMContext) -> None:
    await state.clear()
    
    args = command.args
    if args and args.startswith("ref_"):
        inviter_id = args.split("_")[1]
        current_user_id = str(message.from_user.id)
        
        if inviter_id != current_user_id:
            inviter_id_int = int(inviter_id)
            
            # Takliflar sonini 1 taga oshiramiz
            current_count = referrals_db.get(inviter_id_int, 0) + 1
            referrals_db[inviter_id_int] = current_count
            
            # Taklif qilgan odamga xabar yuborish
            new_user_name = message.from_user.username or message.from_user.first_name
            notif_text = (
                f"🎉 Sizning havolangiz orqali <b>{new_user_name}</b> botga qo'shildi!\n"
                f"👥 Takliflaringiz: <b>{current_count}/5</b>"
            )
            try:
                await message.bot.send_message(chat_id=inviter_id_int, text=notif_text)
            except Exception as e:
                logging.error(f"Xabar yuborishda xatolik: {e}")

    await message.answer(
        "Assalomu alaykum! Tilni tanlang / Выберите язык / Select language:",
        reply_markup=lang_keyboard()
    )

@dp.callback_query(F.data.startswith("lang_"))
async def process_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if callback.data == "lang_ru":
        lang = "ru"
        text = "Вы выбрали русский язык."
    elif callback.data == "lang_en":
        lang = "en"
        text = "You selected English."
    else:
        lang = "uz"
        text = "Siz o'zbek tilini tanladingiz."
        
    await state.update_data(lang=lang)
    await callback.message.answer(text, reply_markup=main_menu(lang))

@dp.message(F.text.in_(["Portfolio", "Portfel"]))
async def show_portfolio(message: Message):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Modern Villa", callback_data="port_villa")],
        [InlineKeyboardButton(text="Interior Design", callback_data="port_interior")],
        [InlineKeyboardButton(text="Landscape", callback_data="port_landscape")]
    ])
    await message.answer("Loyihani tanlang:", reply_markup=inline_kb)

@dp.callback_query(F.data.startswith("port_"))
async def process_portfolio_callback(callback: CallbackQuery):
    await callback.answer()
    if callback.data == "port_villa":
        photo_url = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c"
        text = "Loyiha: Modern Villa\nMaydoni: 220 m2"
    elif callback.data == "port_interior":
        photo_url = "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6"
        text = "Loyiha: Penthouse Interior\nMaydoni: 140 m2"
    else:
        photo_url = "https://images.unsplash.com/photo-1558485561-8041db522f62"
        text = "Loyiha: Landscape\nMaydoni: 6 sotix"
    
    await callback.message.answer_photo(photo=photo_url, caption=text)

# 🎁 REFERALLAR BO'LIMI
@dp.message(F.text.in_(["🎁 Referallarim", "🎁 Рефералы", "🎁 Referrals"]))
async def show_referrals(message: Message):
    user_id = message.from_user.id
    bot_info = await message.bot.get_me()
    ref_count = referrals_db.get(user_id, 0)
    
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    
    text = (
        f"🎁 <b>Sizning taklif havolangiz:</b>\n"
        f"<code>{ref_link}</code>\n\n"
        f"👥 Taklif qilgan do'stlaringiz: <b>{ref_count}/5 ta</b>\n\n"
        f"<i>Aksiya shartiga ko'ra kamida 5 ta do'stingizni taklif qiling va 3 oylik Telegram Premium yutib olish imkoniyatiga ega bo'ling!</i>"
    )
    await message.answer(text)

# 🧮 KALKULYATOR
@dp.message(F.text.in_(["🧮 Narxni hisoblash", "🧮 Калькулятор", "🧮 Calculator"]))
async def start_calc(message: Message, state: FSMContext):
    await state.set_state(CalcForm.calc_type)
    calc_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Xususiy uy / Villa ($15/m²)", callback_data="calc_villa")],
        [InlineKeyboardButton(text="Interyer dizayn / Interior ($20/m²)", callback_data="calc_interior")],
        [InlineKeyboardButton(text="Landshaft / Landscape ($10/m²)", callback_data="calc_landscape")]
    ])
    await message.answer("Hisoblamoqchi bo'lgan yo'nalishni tanlang:", reply_markup=calc_kb)

@dp.callback_query(F.data.startswith("calc_"))
async def process_calc_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    rates = {
        "calc_villa": 15,
        "calc_interior": 20,
        "calc_landscape": 10
    }
    rate = rates.get(callback.data, 15)
    await state.update_data(rate=rate)
    await state.set_state(CalcForm.calc_area)
    
    area_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="100 m²", callback_data="carea_100"), InlineKeyboardButton(text="150 m²", callback_data="carea_150")],
        [InlineKeyboardButton(text="200 m²", callback_data="carea_200"), InlineKeyboardButton(text="300 m²", callback_data="carea_300")]
    ])
    await callback.message.answer("Taxminiy maydonni tanlang:", reply_markup=area_kb)

@dp.callback_query(F.data.startswith("carea_"))
async def process_calc_result(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    areas = {
        "carea_100": 100,
        "carea_150": 150,
        "carea_200": 200,
        "carea_300": 300
    }
    area = areas.get(callback.data, 100)
    data = await state.get_data()
    rate = data.get("rate", 15)
    total_price = area * rate
    
    await state.clear()
    result_text = f"🧮 <b>Hisob-kitob natijasi:</b>\n\n• Maydon: {area} m²\n• 1 m² narxi: ${rate}\n• <b>Taxminiy umumiy qiymat:</b> ${total_price}\n\n<i>Eslatma: Aniq narx ob'ekt murakkabligiga qarab o'zgarishi mumkin.</i>"
    await callback.message.answer(result_text)

@dp.message(F.text.in_(["Savollar", "FAQ"]))
async def show_faq(message: Message):
    await message.answer("Savollar va javoblar bo'limi.")

@dp.message(F.text.in_(["Bog'lanish", "Aloqa", "Contact"]))
async def show_contact(message: Message):
    await message.answer(f"Admin: {ADMIN_USERNAME}")

@dp.message(F.text.in_(["Buyurtma berish", "Zakaz qilish", "Order Project"]))
async def start_order(message: Message, state: FSMContext):
    await state.set_state(OrderForm.project_type)
    type_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Xususiy uy", callback_data="type_villa")],
        [InlineKeyboardButton(text="Interyer", callback_data="type_interior")],
        [InlineKeyboardButton(text="Landshaft", callback_data="type_landscape")]
    ])
    await message.answer("Loyiha turini tanlang:", reply_markup=type_kb)

@dp.callback_query(F.data.startswith("type_"))
async def process_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    types_map = {
        "type_villa": "Xususiy uy",
        "type_interior": "Interyer",
        "type_landscape": "Landshaft"
    }
    await state.update_data(project_type=types_map.get(callback.data))
    await state.set_state(OrderForm.area)
    
    area_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="100 m2 gacha", callback_data="area_small")],
        [InlineKeyboardButton(text="100 - 200 m2", callback_data="area_medium")],
        [InlineKeyboardButton(text="200 m2 dan kop", callback_data="area_large")]
    ])
    await callback.message.answer("Maydonni tanlang:", reply_markup=area_kb)

@dp.callback_query(F.data.startswith("area_"))
async def process_area(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    areas_map = {
        "area_small": "100 m2 gacha",
        "area_medium": "100 - 200 m2",
        "area_large": "200 m2 dan kop"
    }
    await state.update_data(area=areas_map.get(callback.data))
    await state.set_state(OrderForm.phone)
    
    phone_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await callback.message.answer("Telefon raqamingizni yuboring:", reply_markup=phone_kb)

@dp.message(OrderForm.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.clear()
    
    summary = f"Buyurtma qabul qilindi!\nTur: {data['project_type']}\nMaydon: {data['area']}\nTelefon: {phone}"
    await message.answer(summary, reply_markup=main_menu(lang))

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())