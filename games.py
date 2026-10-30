import asyncio
import random
import time
from collections import Counter

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from keyboards import (
    GAMES,
    main_keyboard,
    navigation_keyboard,
    ttt_keyboard,
)

router = Router()


# Har bir foydalanuvchining o‘yini alohida holatda saqlanadi.
class GameState(StatesGroup):
    math = State()
    guess = State()
    scramble = State()
    quiz = State()
    memory = State()
    reaction = State()
    ttt = State()
    rps = State()
    hangman = State()
    mastermind = State()


def game_title(game):
    return GAMES.get(game, "🎮 O‘yin")


async def finish(message: Message, text: str):
    await message.answer(
        text,
        reply_markup=navigation_keyboard(),
    )


async def show_menu(message: Message):
    await message.answer(
        "🎮 **10 ta o‘yin markazi**\n\n"
        "O‘yinni tanlang yoki tasodifiy o‘yin boshlang!",
        reply_markup=main_keyboard(),
        parse_mode="Markdown",
    )


async def start_game(
    message: Message,
    state: FSMContext,
    game: str,
    bot: Bot,
):
    await state.clear()

    # Matematik duel
    if game == "math":
        await state.set_state(GameState.math)
        await state.update_data(score=0, question=0)
        await math_question(message, state)
        return

    # Sonni topish
    if game == "guess":
        secret = random.randint(1, 100)

        await state.set_state(GameState.guess)
        await state.update_data(
            secret=secret,
            attempts=7,
        )

        await message.answer(
            "🔢 **Sonni topish**\n\n"
            "Men 1 dan 100 gacha son o‘yladim.\n"
            "Uni 7 ta urinishda toping.\n\n"
            "Taxminingizni yozing:",
            parse_mode="Markdown",
        )
        return

    # Aralash so‘z
    if game == "scramble":
        words = [
            ("algoritm", "Masalani yechish ketma-ketligi"),
            ("kompyuter", "Elektron hisoblash qurilmasi"),
            ("klaviatura", "Matn kiritish qurilmasi"),
            ("internet", "Butunjahon tarmog‘i"),
            ("dasturchi", "Dastur yozadigan mutaxassis"),
            ("xavfsizlik", "Himoyalanganlik holati"),
            ("mahsulot", "Sotiladigan tovar"),
        ]

        word, hint = random.choice(words)
        letters = list(word)

        while True:
            random.shuffle(letters)
            mixed = "".join(letters)

            if mixed != word:
                break

        await state.set_state(GameState.scramble)
        await state.update_data(
            answer=word,
            hint=hint,
            attempts=3,
        )

        await message.answer(
            f"🔤 **Aralash so‘z**\n\n"
            f"Harflarni to‘g‘ri tartiblang:\n\n"
            f"`{mixed}`\n\n"
            f"💡 Maslahat: {hint}\n"
            "Javobingizni yozing.",
            parse_mode="Markdown",
        )
        return

    # Bilimlar quiz
    if game == "quiz":
        questions = [
            (
                "Python'da ro‘yxat qaysi qavsda yoziladi?",
                ["{}", "[]", "()"],
                1,
            ),
            (
                "HTML nimaga xizmat qiladi?",
                ["Sahifa tuzilishiga", "Ma'lumotlar bazasiga", "Operatsion tizimga"],
                0,
            ),
            (
                "2 ning 5-darajasi nechaga teng?",
                ["10", "25", "32"],
                2,
            ),
            (
                "Git nima?",
                ["Brauzer", "Versiya nazorati tizimi", "Matn muharriri"],
                1,
            ),
            (
                "SQL orqali ma'lumot olish buyrug‘i?",
                ["SELECT", "PUSH", "START"],
                0,
            ),
            (
                "CPU nimani anglatadi?",
                ["Central Processing Unit", "Computer Power Utility", "Core Program User"],
                0,
            ),
            (
                "Java'da obyekt yaratish uchun ko‘pincha qaysi kalit so‘z ishlatiladi?",
                ["make", "new", "object"],
                1,
            ),
        ]

        random.shuffle(questions)
        await state.set_state(GameState.quiz)
        await state.update_data(
            questions=questions[:5],
            index=0,
            score=0,
        )

        await quiz_question(message, state)
        return

    # Xotira sinovi
    if game == "memory":
        digits = "".join(
            str(random.randint(0, 9))
            for _ in range(7)
        )

        await state.set_state(GameState.memory)
        await state.update_data(answer=digits)

        await message.answer(
            "👁 **Xotira sinovi**\n\n"
            "Raqamlarni 5 soniya eslab qoling:\n\n"
            f"`{' '.join(digits)}`",
            parse_mode="Markdown",
        )

        async def hide_digits():
            await asyncio.sleep(5)

            if await state.get_state() == GameState.memory.state:
                await bot.send_message(
                    message.chat.id,
                    "Endi eslab qolgan 7 ta raqamni "
                    "bo‘sh joysiz yozing.",
                )

        asyncio.create_task(hide_digits())
        return

    # Reaksiya testi
    if game == "reaction":
        await state.set_state(GameState.reaction)
        await state.update_data(phase="waiting")

        await message.answer(
            "⚡ **Reaksiya testi**\n\n"
            "Yashil tugma paydo bo‘lguncha kuting.\n"
            "Erta bosmang!"
        )

        async def reaction_timer():
            await asyncio.sleep(random.uniform(2.5, 6))

            data = await state.get_data()

            if (
                await state.get_state() != GameState.reaction.state
                or data.get("phase") != "waiting"
            ):
                return

            await state.update_data(
                phase="ready",
                started_at=time.perf_counter(),
            )

            try:
                await bot.send_message(
                    message.chat.id,
                    "🟢 HOZIR BOSING!",
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[[
                            InlineKeyboardButton(
                                text="⚡ BOSISH!",
                                callback_data="reaction:click",
                            )
                        ]]
                    ),
                )
            except Exception:
                pass

        asyncio.create_task(reaction_timer())
        return

    # X-O
    if game == "ttt":
        board = [" "] * 9

        await state.set_state(GameState.ttt)
        await state.update_data(board=board)

        await message.answer(
            "❌⭕ **X-O**\n"
            "Siz ❌, bot esa ⭕.\n"
            "Katakni tanlang:",
            reply_markup=ttt_keyboard(board),
            parse_mode="Markdown",
        )
        return

    # Tosh-qaychi-qog‘oz
    if game == "rps":
        await state.set_state(GameState.rps)
        await state.update_data(
            player_score=0,
            bot_score=0,
            round=1,
        )

        await rps_question(message, state)
        return

    # So‘z topish
    if game == "hangman":
        word = random.choice([
            "python",
            "telegram",
            "algoritm",
            "kompyuter",
            "dasturchi",
            "internet",
        ])

        await state.set_state(GameState.hangman)
        await state.update_data(
            word=word,
            used=[],
            mistakes=0,
        )

        await hangman_screen(message, state)
        return

    # Mastermind
    if game == "mastermind":
        code = "".join(
            random.sample("0123456789", 4)
        )

        await state.set_state(GameState.mastermind)
        await state.update_data(
            code=code,
            attempts=8,
        )

        await message.answer(
            "🔐 **Mastermind**\n\n"
            "4 ta takrorlanmaydigan raqamdan "
            "iborat kodni toping.\n\n"
            "Masalan: `5831`\n"
            "Sizda 8 ta urinish bor.\n"
            "Taxminingizni yuboring.",
            parse_mode="Markdown",
        )


# Tasodifiy yoki tanlangan o‘yin
@router.callback_query(F.data.startswith("game:"))
async def game_selected(
    call: CallbackQuery,
    state: FSMContext,
    bot: Bot,
):
    game = call.data.split(":", 1)[1]

    if game == "random":
        game = random.choice(list(GAMES.keys()))

    await call.answer()

    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await call.message.answer(f"Tanlangan o‘yin: {game_title(game)}")
    await start_game(call.message, state, game, bot)


@router.callback_query(F.data == "menu")
async def menu_callback(
    call: CallbackQuery,
    state: FSMContext,
):
    await state.clear()
    await call.answer()

    await call.message.answer(
        "🎮 Bosh menyu:",
        reply_markup=main_keyboard(),
    )


@router.message(Command("menu"))
async def menu_command(
    message: Message,
    state: FSMContext,
):
    await state.clear()
    await show_menu(message)


# 1. MATEMATIK DUEL
async def math_question(message: Message, state: FSMContext):
    data = await state.get_data()
    number = data.get("question", 0) + 1

    if number > 5:
        score = data.get("score", 0)
        await state.clear()

        await finish(
            message,
            f"🧮 O‘yin tugadi!\n\n"
            f"Natija: {score}/5\n"
            f"Foiz: {score * 20}%",
        )
        return

    a = random.randint(10, 60)
    b = random.randint(2, 20)
    operator = random.choice(["+", "-", "*"])

    if operator == "+":
        answer = a + b
    elif operator == "-":
        answer = a - b
    else:
        answer = a * b

    await state.update_data(
        question=number,
        math_answer=answer,
    )

    await message.answer(
        f"🧮 **Matematik duel**\n"
        f"Savol: {number}/5\n\n"
        f"`{a} {operator} {b} = ?`\n\n"
        "Javobni son bilan yozing.",
        parse_mode="Markdown",
    )


@router.message(GameState.math)
async def math_answer(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().lstrip("-").isdigit():
        await message.answer("Javobni butun son ko‘rinishida yuboring.")
        return

    data = await state.get_data()
    correct = int(message.text) == data["math_answer"]
    score = data.get("score", 0) + int(correct)

    await state.update_data(score=score)

    await message.answer(
        "✅ To‘g‘ri!" if correct
        else f"❌ Noto‘g‘ri. Javob: {data['math_answer']}"
    )

    await math_question(message, state)


# 2. SONNI TOPISH
@router.message(GameState.guess)
async def guess_answer(message: Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("Iltimos, butun son kiriting.")
        return

    number = int(message.text)

    if not 1 <= number <= 100:
        await message.answer("Son 1 dan 100 gacha bo‘lishi kerak.")
        return

    data = await state.get_data()
    secret = data["secret"]

    if number == secret:
        await state.clear()
        await finish(message, f"🎉 Tabriklayman! Yashirin son {secret} edi.")
        return

    attempts = data["attempts"] - 1

    if attempts <= 0:
        await state.clear()
        await finish(message, f"Urinishlar tugadi. Yashirin son: {secret}")
        return

    await state.update_data(attempts=attempts)

    hint = "kattaroq" if number < secret else "kichikroq"

    await message.answer(
        f"❌ Yashirin son bundan {hint}.\n"
        f"Qolgan urinishlar: {attempts}"
    )


# 3. ARALASH SO‘Z
@router.message(GameState.scramble)
async def scramble_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    answer = data["answer"]

    if (message.text or "").strip().casefold() == answer.casefold():
        await state.clear()
        await finish(message, f"🎉 To‘g‘ri! So‘z: {answer}")
        return

    attempts = data["attempts"] - 1

    if attempts <= 0:
        await state.clear()
        await finish(message, f"Urinish tugadi. To‘g‘ri javob: {answer}")
        return

    await state.update_data(attempts=attempts)

    await message.answer(
        f"❌ Xato. Yana urinib ko‘ring.\n"
        f"Maslahat: {data['hint']}\n"
        f"Qolgan urinish: {attempts}"
    )


# 4. BILIMLAR QUIZ
async def quiz_question(message: Message, state: FSMContext):
    data = await state.get_data()
    index = data["index"]

    if index >= len(data["questions"]):
        score = data["score"]
        await state.clear()

        await finish(
            message,
            f"🧠 Quiz tugadi!\nNatija: {score}/5"
        )
        return

    question, options, correct = data["questions"][index]

    await state.update_data(correct=correct)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=option,
                    callback_data=f"quiz:{i}",
                )
            ]
            for i, option in enumerate(options)
        ]
    )

    await message.answer(
        f"🧠 **Quiz**\nSavol {index + 1}/5\n\n{question}",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@router.callback_query(GameState.quiz, F.data.startswith("quiz:"))
async def quiz_answer(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    picked = int(call.data.split(":")[1])
    correct = data["correct"]

    score = data["score"] + int(picked == correct)

    await state.update_data(
        score=score,
        index=data["index"] + 1,
    )

    await call.answer(
        "✅ To‘g‘ri!" if picked == correct else "❌ Noto‘g‘ri",
        show_alert=True,
    )

    await quiz_question(call.message, state)


# 5. XOTIRA SINOVI
@router.message(GameState.memory)
async def memory_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    answer = data["answer"]

    guess = "".join((message.text or "").split())

    await state.clear()

    if guess == answer:
        await finish(message, "🧠 Ajoyib! Raqamlarni to‘g‘ri eslab qoldingiz.")
    else:
        await finish(
            message,
            f"Xotira sinovi yakunlandi.\n"
            f"To‘g‘ri javob: {answer}"
        )


# 6. REAKSIYA TESTI
@router.callback_query(
    GameState.reaction,
    F.data == "reaction:click",
)
async def reaction_click(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data.get("phase") != "ready":
        await call.answer("Hali emas! Yashil signalni kuting.", show_alert=True)
        return

    elapsed = time.perf_counter() - data["started_at"]

    await state.clear()
    await call.answer()

    await call.message.answer(
        f"⚡ Reaksiya vaqtingiz: {elapsed:.3f} soniya",
        reply_markup=navigation_keyboard(),
    )


# 7. X-O
def ttt_winner(board):
    lines = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6),
    ]

    for a, b, c in lines:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]

    return None


@router.callback_query(GameState.ttt, F.data.startswith("ttt:"))
async def ttt_move(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    board = data["board"]

    index = int(call.data.split(":")[1])

    if board[index] != " ":
        await call.answer("Bu katak band.", show_alert=True)
        return

    board[index] = "❌"
    winner = ttt_winner(board)

    if winner:
        await state.clear()
        await call.answer()
        await call.message.edit_text(
            "🎉 Siz g‘alaba qozondingiz!",
            reply_markup=navigation_keyboard(),
        )
        return

    if " " not in board:
        await state.clear()
        await call.answer()
        await call.message.edit_text(
            "🤝 Durrang!",
            reply_markup=navigation_keyboard(),
        )
        return

    empty = [i for i, value in enumerate(board) if value == " "]

    # Bot yutadigan yurishni izlaydi, keyin o‘yinchini to‘sadi.
    bot_move = None

    for mark in ["⭕", "❌"]:
        for i in empty:
            test_board = board.copy()
            test_board[i] = mark

            if ttt_winner(test_board) == mark:
                bot_move = i
                break

        if bot_move is not None:
            break

    if bot_move is None:
        priorities = [4, 0, 2, 6, 8, 1, 3, 5, 7]
        bot_move = next(i for i in priorities if i in empty)

    board[bot_move] = "⭕"

    winner = ttt_winner(board)
    await call.answer()

    if winner or " " not in board:
        await state.clear()
        result = "🤖 Bot g‘alaba qozondi!" if winner else "🤝 Durrang!"

        await call.message.edit_text(
            result,
            reply_markup=navigation_keyboard(),
        )
        return

    await state.update_data(board=board)

    await call.message.edit_reply_markup(
        reply_markup=ttt_keyboard(board)
    )


# 8. TOSH-QAYCHI-QOG‘OZ
async def rps_question(message: Message, state: FSMContext):
    data = await state.get_data()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="✊ Tosh", callback_data="rps:rock"),
            InlineKeyboardButton(text="✋ Qog‘oz", callback_data="rps:paper"),
            InlineKeyboardButton(text="✌️ Qaychi", callback_data="rps:scissors"),
        ]]
    )

    await message.answer(
        f"✊ **Tosh-qaychi-qog‘oz**\n"
        f"Raund: {data['round']}/5\n"
        f"Siz: {data['player_score']} — {data['bot_score']} : Bot\n\n"
        "Tanlang:",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@router.callback_query(GameState.rps, F.data.startswith("rps:"))
async def rps_answer(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    player = call.data.split(":")[1]
    computer = random.choice(["rock", "paper", "scissors"])

    beats = {
        "rock": "scissors",
        "paper": "rock",
        "scissors": "paper",
    }

    player_score = data["player_score"]
    bot_score = data["bot_score"]

    if player != computer:
        if beats[player] == computer:
            player_score += 1
            result = "Siz raundda yutdingiz!"
        else:
            bot_score += 1
            result = "Bot raundda yutdi!"
    else:
        result = "Raund durang!"

    await call.answer(
        f"{result}\nBot: {computer}",
        show_alert=True,
    )

    round_number = data["round"]

    if round_number >= 5:
        await state.clear()

        if player_score > bot_score:
            winner = "🏆 Siz g‘olibsiz!"
        elif bot_score > player_score:
            winner = "🤖 Bot g‘olib bo‘ldi."
        else:
            winner = "🤝 Turnir durang bilan tugadi."

        await call.message.answer(
            f"Turnir natijasi:\n"
            f"Siz: {player_score}\n"
            f"Bot: {bot_score}\n\n"
            f"{winner}",
            reply_markup=navigation_keyboard(),
        )
        return

    await state.update_data(
        player_score=player_score,
        bot_score=bot_score,
        round=round_number + 1,
    )

    await rps_question(call.message, state)


# 9. SO‘Z TOPISH
async def hangman_screen(message: Message, state: FSMContext):
    data = await state.get_data()

    word = data["word"]
    used = data["used"]
    mistakes = data["mistakes"]

    display = " ".join(
        letter.upper() if letter in used else "_"
        for letter in word
    )

    if all(letter in used for letter in word):
        await state.clear()
        await finish(message, f"🎉 G‘alaba! So‘z: {word.upper()}")
        return

    if mistakes >= 6:
        await state.clear()
        await finish(message, f"Urinish tugadi. So‘z: {word.upper()}")
        return

    letters = "abcdefghijklmnopqrstuvwxyz"
    available = [letter for letter in letters if letter not in used]

    rows = []

    for i in range(0, len(available), 7):
        rows.append([
            InlineKeyboardButton(
                text=letter.upper(),
                callback_data=f"hang:{letter}",
            )
            for letter in available[i:i + 7]
        ])

    rows.append([
        InlineKeyboardButton(
            text="🎮 Menyu",
            callback_data="menu",
        )
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    text = (
        f"🪢 **So‘z topish**\n\n"
        f"So‘z: `{display}`\n"
        f"Xatolar: {mistakes}/6"
    )

    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@router.callback_query(GameState.hangman, F.data.startswith("hang:"))
async def hangman_letter(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    letter = call.data.split(":")[1]

    used = data["used"]

    if letter in used:
        await call.answer("Bu harf avval tanlangan.")
        return

    used.append(letter)

    mistakes = data["mistakes"]

    if letter not in data["word"]:
        mistakes += 1

    await state.update_data(
        used=used,
        mistakes=mistakes,
    )

    await call.answer(
        "Harf topildi!" if letter in data["word"] else "Bu harf yo‘q."
    )

    await hangman_screen(call.message, state)


# 10. MASTERMIND
@router.message(GameState.mastermind)
async def mastermind_answer(message: Message, state: FSMContext):
    guess = (message.text or "").strip()

    if (
        len(guess) != 4
        or not guess.isdigit()
        or len(set(guess)) != 4
    ):
        await message.answer(
            "4 ta takrorlanmaydigan raqam yuboring. Masalan: 5831"
        )
        return

    data = await state.get_data()
    code = data["code"]

    if guess == code:
        await state.clear()
        await finish(message, "🔐 Ajoyib! Maxfiy kodni topdingiz.")
        return

    attempts = data["attempts"] - 1

    if attempts <= 0:
        await state.clear()
        await finish(message, f"Urinishlar tugadi. Kod: {code}")
        return

    exact = sum(
        guess[i] == code[i]
        for i in range(4)
    )

    guess_counts = Counter(guess)
    code_counts = Counter(code)

    common = sum(
        min(guess_counts[digit], code_counts[digit])
        for digit in guess_counts
    )

    misplaced = common - exact

    await state.update_data(attempts=attempts)

    await message.answer(
        "🔐 Natija:\n"
        f"Joyida turgan raqamlar: {exact}\n"
        f"Boshqa joydagi raqamlar: {misplaced}\n"
        f"Qolgan urinishlar: {attempts}"
    )