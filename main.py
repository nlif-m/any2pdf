import asyncio
import logging
import sys
from os import getenv
import xmlrpc.client

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, BufferedInputFile
from aiogram import F
import unoserver.client


TOKEN = getenv("TGTOKEN")
ALLOWED_USERS = set(map(int, getenv("TGUSERS").split(",")))
UNO_CLIENT_SERVER = getenv("UNO_SERVER", "127.0.0.1")
UNO_CLIENT_SERVER_PORT = getenv("UNO_SERVER_PORT", "2003")

dp = Dispatcher()

UNO_CLIENT = unoserver.client.UnoClient(
    server=UNO_CLIENT_SERVER, port=UNO_CLIENT_SERVER_PORT, host_location="remote"
)
print(f"UNO_CLIENT({UNO_CLIENT.server=}, {UNO_CLIENT.port=})")


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    print(message.from_user)
    await message.answer(
        f"Hello, {html.bold(message.from_user.full_name)}: {html.bold(message.from_user.id)}!\n"
        f"Send me any document and I will try to convert in to pdf!"
    )


@dp.message(F.document, F.from_user.id.in_(ALLOWED_USERS))
async def converter_handler(message: Message) -> None:
    """
    This handler will receive a document ant try to convert it to pdf
    """
    assert message.document is not None
    doc = message.document

    assert message.bot is not None
    f = await message.bot.download(doc)
    if f is None:
        await message.answer("Failed to download your document, try send again")
        return
    data = f.read()
    try:
        pdf: bytes = UNO_CLIENT.convert(indata=data, convert_to="pdf")
    except xmlrpc.client.Fault as e:
        print(e)
        await message.answer("Failed to convert your document, try send again")
        return

    pdf_file = BufferedInputFile(pdf, filename=f"{doc.file_name}.pdf")
    await message.answer_document(pdf_file)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    print(f"Starting bot with users: {ALLOWED_USERS}")
    asyncio.run(main())
