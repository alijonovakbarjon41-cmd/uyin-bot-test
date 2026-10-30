from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

GAMES = {
    "math": "🧮 Matematik duel",
    "guess": "🔢 Sonni topish",
    "scramble": "🔤 Aralash so‘z",
    "quiz": "🧠 Bilimlar quiz",
    "memory": "👁 Xotira sinovi",
    "reaction": "⚡ Reaksiya testi",
    "ttt": "❌⭕ X-O",
    "rps": "✊ Tosh-qaychi-qog‘oz",
    "hangman": "🪢 So‘z topish",
    "mastermind": "🔐 Mastermind",
}


def main_keyboard():
    buttons = []

    items = list(GAMES.items())

    for i in range(0, len(items), 2):
        row = [
            InlineKeyboardButton(
                text=items[i][1],
                callback_data=f"game:{items[i][0]}",
            )
        ]

        if i + 1 < len(items):
            row.append(
                InlineKeyboardButton(
                    text=items[i + 1][1],
                    callback_data=f"game:{items[i + 1][0]}",
                )
            )

        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(
            text="🎲 Tasodifiy o‘yin",
            callback_data="game:random",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def navigation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Yana o‘ynash",
                    callback_data="game:random",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎮 Bosh menyu",
                    callback_data="menu",
                )
            ],
        ]
    )


def ttt_keyboard(board):
    rows = []

    for row_index in range(3):
        row = []

        for col_index in range(3):
            index = row_index * 3 + col_index
            value = board[index]

            if value == " ":
                value = str(index + 1)

            row.append(
                InlineKeyboardButton(
                    text=value,
                    callback_data=f"ttt:{index}",
                )
            )

        rows.append(row)

    rows.append([
        InlineKeyboardButton(
            text="🎮 Menyu",
            callback_data="menu",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)