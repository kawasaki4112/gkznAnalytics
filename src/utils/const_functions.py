import re
from aiogram.types import (InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup,
                           CopyTextButton)


def rkb(text: str) -> KeyboardButton:
    return KeyboardButton(text=text)


def ikb(
        text: str,
        callback_data: str = None,
        url: str = None,
        copy: str = None,
) -> InlineKeyboardButton:
    if callback_data is not None:
        return InlineKeyboardButton(text=text, callback_data=callback_data)
    elif url is not None:
        return InlineKeyboardButton(text=text, url=url)
    elif copy is not None:
        return InlineKeyboardButton(text=text, copy_text=CopyTextButton(text=copy))
