import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes

# --- AYARLAR ---
TOKEN = "8442385792:AAFgka41gY4qRJxq6LGSB8kQhGbhhGmV1mo"
ADMIN_ID = 7979504487
KANALLAR = ["@LBduyuru", "@LiderBeyChat", "@lbguvence"]

# Görev Listesi
GOREVLER = [
    ("🔥 Görev 1", "https://lnk.news/YkAD"), ("⚡ Görev 2", "https://lnk.news/f78PaU"),
    ("💎 Görev 3", "https://lnk.news/mhF3T"), ("🚀 Görev 4", "https://lnk.news/Rtke5x"),
    ("✏️ Görev 5", "https://lnk.news/6UK"), ("🌪️ Görev 6", "https://lnk.news/fuCqfP"),
    ("✨ Görev 7", "https://lnk.news/JKmy4"), ("💰 Görev 8", "https://lnk.news/V6TE"),
    ("🏁 Görev 9", "https://lnk.news/6iQ01m"), ("✅ Görev 10", "https://lnk.news/nvTk")
]

# Şifreler ve Puanları
SIFRE_DB = {
    "AKREP44": 50, "KAPLAN44": 50, "MASA531": 50, "LIDER5380": 50, 
    "KALEM2": 50, "FIRTINA61": 50, "ELMAS07": 50, "MİLYONER88": 50, 
    "SON1": 50, "BİTTİ0": 50
}

# Market Paketleri
PAKETLER = {
    "t100": ("👤 100 Takipçi", 1000), "t500": ("👤 500 Takipçi", 4500),
    "t1000": ("👤 1000 Takipçi", 8000), "b100": ("❤️ 100 Beğeni", 500),
    "b500": ("❤️ 500 Beğeni", 2000), "b1000": ("❤️ 1000 Beğeni", 3500)
}

users = {}

def get_u(uid):
    if uid not in users: 
        users[uid] = {'stars': 0, 'refs': 0, 'used': [], 'step': None, 'temp_order': {}}
    return users[uid]

async def check_sub(uid, context):
    for kanal in KANALLAR:
        try:
            m = await context.bot.get_chat_member(chat_id=kanal, user_id=uid)
            if m.status in ['left', 'kicked']: return False
        except: return False
    return True

def main_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 MARKET", callback_data="market"), InlineKeyboardButton("👤 PROFİL", callback_data="p")],
        [InlineKeyboardButton("📜 GÖREV LİSTESİ", callback_data="tasks")],
        [InlineKeyboardButton("🔗 REFERANS", callback_data="ref"), InlineKeyboardButton("🔑 KOD GİR", callback_data="kod")]
    ])

async def start(update, context):
    uid = update.effective_user.id
    u = get_u(uid)
    
    if not await check_sub(uid, context):
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Kanallara Katıldım", callback_data="check_subs")]])
        txt = "🚨 **DUR KANKA!**\n\nSistemi kullanmak için şu 3 kanala katılman zorunlu:\n1- @LBduyuru\n2- @LiderBeyChat\n3- @lbguvence"
        if update.message: await update.message.reply_text(txt, reply_markup=kb)
        else: await update.callback_query.edit_message_text(txt, reply_markup=kb)
        return

    if context.args and context.args[0].isdigit():
        rid = int(context.args[0])
        if rid != uid and rid in users and uid not in users[rid].get('ref_list', []):
            users[rid]['stars'] += 100
            users[rid]['refs'] += 1
            if 'ref_list' not in users[rid]: users[rid]['ref_list'] = []
            users[rid]['ref_list'].append(uid)

    txt = "👑 **LiderBey İnstagram Hizmetlerine Hoş Geldin! Görev Yaparak ⭐️ kazanırsınız ve bu ⭐️ ile marketten istediğinizi Alabilirsiniz. Eğer bizim takipçi gönderdiğimize inanmiyorsanız güvence kanalımıza göz atabilirsiniz**\nHer işlemde menüden devam edebilirsin.\n\n⚠️Unutmayın: Takipçilerimiz garantili değildir düşüş olabilir."
    if update.message: await update.message.reply_text(txt, reply_markup=main_kb())
    else: await update.callback_query.edit_message_text(txt, reply_markup=main_kb())

async def q_handler(update, context):
    q = update.callback_query; uid = q.from_user.id; u = get_u(uid); await q.answer()
    
    if q.data == "check_subs":
        if await check_sub(uid, context): await start(update, context)
        else: await q.edit_message_text("❌ Kanallara hala katılmamışsın!")

    elif q.data == "market":
        kb = [[InlineKeyboardButton(f"{v[0]} - {v[1]}⭐", callback_data=f"buy_{k}")] for k, v in PAKETLER.items()]
        kb.append([InlineKeyboardButton("🏠 Ana Menü", callback_data="back")])
        await q.edit_message_text("🛍 **Paket Seçimi**\nUnutma: Takipçilerde garanti yoktur, düşüş olabilir!", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data.startswith("buy_"):
        pid = q.data.split("_")[1]
        p_name, p_price = PAKETLER[pid]
        if u['stars'] < p_price:
            await q.message.reply_text("❌ Yetersiz bakiye!")
            return
        u['temp_order'] = {'pid': pid}
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Onayla", callback_data="confirm_p")],
            [InlineKeyboardButton("❌ Vazgeç", callback_data="market")]
        ])
        await q.edit_message_text(f"❓ **{p_name}** almak istiyor musun?\nFiyat: {p_price}⭐", reply_markup=kb)

    elif q.data == "confirm_p":
        u['step'] = "get_insta"
        await q.edit_message_text("📸 **Instagram Kullanıcı Adını Yaz:**\n(@ kullanmadan yazın)")

    elif q.data == "tasks":
        kb = [[InlineKeyboardButton(n, url=url)] for n, url in GOREVLER]
        kb.append([InlineKeyboardButton("⬅️ Geri", callback_data="back")])
        await q.edit_message_text("📜 **Aşağıdaki linklerde şifre bulunmaktadır bulduğunuz şifreyi Kod gir butonuna basarak kodu girin kodunuz dogruysa +50⭐️ kazanırsınız iyi görevler!**", reply_markup=InlineKeyboardMarkup(kb))

    elif q.data == "p":
        await q.edit_message_text(f"👤 **Profil Bilgilerin**\nID: `{uid}`\n⭐ Bakiye: {u['stars']}\n👥 Ref: {u['refs']}", reply_markup=main_kb())

    elif q.data == "ref":
        b = await context.bot.get_me()
        await q.edit_message_text(f"🔗 **Referans Linkin:** `https://t.me/{b.username}?start={uid}`\n\nHer arkadaşın için **100⭐** kazan!", reply_markup=main_kb())

    elif q.data == "kod":
        u['step'] = "enter_code"
        await q.edit_message_text("🔑 **Görev listesindeki linklerden aldıgın kodları buraya yaz ve 50⭐ kap:**")

    elif q.data == "back": await start(update, context)

    elif q.data.startswith("adm_onay_"):
        cid = q.data.split("_")[2]
        await context.bot.send_message(chat_id=cid, text="✅ **Siparişiniz admin tarafından onaylandı!** En kısa sürede Siparişiniz tamamlanacaktır.")
        await q.edit_message_text(f"Sipariş {cid} onaylandı.")
    
    elif q.data.startswith("adm_red_"):
        cid = q.data.split("_")[2]
        context.user_data['red_id'] = cid
        await q.message.reply_text(f"Sipariş {cid} için RED sebebini yazın:")

async def msg_handler(update, context):
    uid = update.effective_user.id; u = get_u(uid); text = update.message.text
    
    if uid == ADMIN_ID and 'red_id' in context.user_data:
        rid = context.user_data.pop('red_id')
        await context.bot.send_message(chat_id=rid, text=f"❌ **Siparişiniz Reddedildi!**\nSebep: {text}")
        await update.message.reply_text("Red sebebi kullanıcıya iletildi.")
        return

    if u['step'] == "enter_code":
        code = text.strip().upper()
        if code in SIFRE_DB:
            if code not in u['used']:
                u['stars'] += 50
                u['used'].append(code)
                await update.message.reply_text("✅ Kod doğru! +50⭐ hesabına yüklendi.", reply_markup=main_kb())
            else:
                await update.message.reply_text("❌ Bu kodu zaten kullanmışsın!", reply_markup=main_kb())
        else:
            await update.message.reply_text("❌ Hatalı şifre!", reply_markup=main_kb())
        u['step'] = None

    elif u['step'] == "get_insta":
        u['temp_order']['insta'] = text
        u['step'] = "get_note"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Vazgeç", callback_data="market")]])
        await update.message.reply_text("📝 **Siparişinizin daha hızlı gelmesi için lütfen Siparişi notunuzu yazın**\n(Eğer not yazmassanız Siparişiniz oluşmaz)", reply_markup=kb)

    elif u['step'] == "get_note":
        note = text if text.lower() != "hayır" else "Yok"
        pid = u['temp_order']['pid']; p_name, p_price = PAKETLER[pid]
        u['stars'] -= p_price
        
        warn = (
            "⚠️ **INSTAGRAMDAN ŞU AYARLARI KESİNLİKLE YAP:**\n\n"
            "1- Ayarlar > Hesap Gizliliği > **Açık yap**\n"
            "2- Ayarlar > Arkadaşları takip et ve davet > Değerlendirilmesi için işaretle > **Kapat**\n\n"
            "✅ Siparişin admin panelimize düştü!"
        )
        await update.message.reply_text(warn, reply_markup=main_kb())

        admin_msg = (
            f"🔔 **YENİ SİPARİŞ!**\n\n"
            f"👤 **Telegram Hesabı:** @{update.effective_user.username} & ID: `{uid}`\n"
            f"📸 **İnstagram Hesabı:** @{u['temp_order']['insta']}\n"
            f"📦 **Ne Sipariş Etti:** {p_name}\n"
            f"📝 **Not:** {note}"
        )
        akb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Onayla", callback_data=f"adm_onay_{uid}"), InlineKeyboardButton("❌ Reddet", callback_data=f"adm_red_{uid}")]
        ])
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, reply_markup=akb)
        u['step'] = None

async def puan_ekle(update, context):
    if update.effective_user.id != ADMIN_ID: return
    try:
        tid = int(context.args[0]); amt = int(context.args[1])
        u = get_u(tid); u['stars'] += amt
        await update.message.reply_text(f"✅ {tid} ID'sine {amt}⭐ eklendi.")
        await context.bot.send_message(chat_id=tid, text=f"🎁 Admin hesabınıza {amt}⭐ ekledi!")
    except:
        await update.message.reply_text("Kullanım: `/puanekle ID Miktar` kanka.")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("puanekle", puan_ekle))
    app.add_handler(CallbackQueryHandler(q_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))
    app.run_polling()
