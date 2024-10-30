import json
from pathlib import Path
import subprocess
import sys
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from info import Config, Txt

config_path = Path("config.json")


@Client.on_message(filters.private & filters.user(Config.SUDO) & filters.command('add_account'))
async def add_account(bot: Client, cmd: Message):
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
        else:
            return await cmd.reply_text(text="Anda belum membuat konfigurasi! \n\n Silakan buat konfigurasi dengan menggunakan /make_config", reply_to_message_id=cmd.id)

        try:
            session = await bot.ask(text=Txt.SEND_SESSION_MSG, chat_id=cmd.chat.id, filters=filters.text, timeout=60)
        except:
            await bot.send_message(cmd.from_user.id, "Error!!\n\nWaktu permintaan habis.\nMulai ulang dengan menggunakan /add_account", reply_to_message_id=cmd.id)
            return

        ms = await cmd.reply_text('**Silakan Tunggu...**', reply_to_message_id=cmd.id)

        for account in config['accounts']:
            if account['Session_String'] == session.text:
                return await ms.edit(text=f"**Akun {account['OwnerName']} sudah ada dalam konfigurasi, Anda tidak dapat menambahkan akun yang sama lebih dari satu kali 🤡**\n\n Error !")

        # Jalankan perintah shell dan tangkap outputnya
        try:
            process = subprocess.Popen(
                ["python", f"login.py", f"{config['Target']}", f"{session.text}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as err:
            await bot.send_message(cmd.chat.id, text=f"<b>ERROR :</b>\n<pre>{err}</pre>")
            return

        # Gunakan communicate() untuk berinteraksi dengan proses
        stdout, stderr = process.communicate()
        return_code = process.wait()

        # Periksa kode kembali untuk melihat apakah perintah berhasil
        if return_code == 0:
            output_bytes = stdout
            output_string = output_bytes.decode('utf-8').replace('\r\n', '\n')
            AccountHolder = json.loads(output_string)
        else:
            return await ms.edit('**Terjadi Kesalahan, Silakan Periksa Input Anda Apakah Sudah Diisi Dengan Benar!**')

        try:
            NewConfig = {
                "Target": config['Target'],
                "accounts": list(config['accounts'])
            }

            new_account = {
                "Session_String": session.text,
                "OwnerUid": AccountHolder['id'],
                "OwnerName": AccountHolder['first_name']
            }
            NewConfig["accounts"].append(new_account)

            with open(config_path, 'w', encoding='utf-8') as file:
                json.dump(NewConfig, file, indent=4)

        except Exception as e:
            print(e)

        await ms.edit(text="**Akun Berhasil Ditambahkan**\n\nKlik tombol di bawah untuk melihat semua akun yang telah Anda tambahkan 👇.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Akun yang Anda Tambahkan', callback_data='account_config')]]))

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


@Client.on_message(filters.private & filters.user(Config.SUDO) & filters.command('target'))
async def target(bot: Client, cmd: Message):
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                config = json.load(file)
        else:
            return await cmd.reply_text(text="Anda belum membuat konfigurasi! \n\n Silakan buat konfigurasi dengan menggunakan /make_config", reply_to_message_id=cmd.id)

        Info = await bot.get_chat(config['Target'])

        btn = [
            [InlineKeyboardButton(text='Ubah Target', callback_data='chgtarget')]
        ]

        text = f"Nama Channel :- <code> {Info.title} </code>\nUsername Channel :- <code> @{Info.username} </code>\nID Chat Channel :- <code> {Info.id} </code>"

        await cmd.reply_text(text=text, reply_to_message_id=cmd.id, reply_markup=InlineKeyboardMarkup(btn))
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


@Client.on_message(filters.private & filters.user(Config.SUDO) & filters.command('del_config'))
async def delete_config(bot: Client, cmd: Message):
    btn = [
        [InlineKeyboardButton(text='Ya', callback_data='delconfig-yes')],
        [InlineKeyboardButton(text='Tidak', callback_data='delconfig-no')]
    ]

    await cmd.reply_text(text="**⚠️ Apakah Anda Yakin?**\n\nAnda ingin menghapus Konfigurasi.", reply_to_message_id=cmd.id, reply_markup=InlineKeyboardMarkup(btn))
