from math import ceil
from typing import Dict, List

from telegram import MAX_MESSAGE_LENGTH, Bot, InlineKeyboardButton, ParseMode, Update
from telegram.error import TelegramError

from scenario import NO_LOAD


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def split_message(msg: str) -> List[str]:
    if len(msg) < MAX_MESSAGE_LENGTH:
        return [msg]

    else:
        lines = msg.splitlines(True)
        big_msg = ""
        result = []
        for line in lines:
            if len(big_msg) + len(line) < MAX_MESSAGE_LENGTH:
                big_msg += line
            else:
                result.append(big_msg)
                big_msg = line
        else:
            # Else statement at the end of the for loop, so append the leftover string.
            result.append(big_msg)

        return result


def paginate_modules(page_n: int, module_dict: Dict, prefix, chat=None) -> List:
    if not chat:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({})".format(
                        prefix, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )
    else:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({},{})".format(
                        prefix, chat, x.__mod_name__.lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )

    pairs = [modules[i * 2 : (i + 1) * 2] for i in range((len(modules) + 2 - 1) // 2)]

    round_num = len(modules) / 2
    calc = len(modules) - round(round_num)
    if calc == 1:
        pairs.append((modules[-1],))
    elif calc == 2:
        pairs.append((modules[-1],))

    max_num_pages = ceil(len(pairs) / 5)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > 6:
        pairs = pairs[modulo_page * 5 : 5 * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "《", callback_data="{}_prev({})".format(prefix, modulo_page)
                ),
                EqInlineKeyboardButton("⇆", callback_data="all_cmds"),
                EqInlineKeyboardButton(
                    "》", callback_data="{}_next({})".format(prefix, modulo_page)
                ),
            )
        ]

    else:
        pairs += [[EqInlineKeyboardButton("⇆ ", callback_data="all_cmds")]]

    return pairs


def send_to_list(
    bot: Bot, send_to: list, message: str, markdown=False, html=False
) -> None:
    if html and markdown:
        raise Exception("Can only send with either markdown or HTML!")
    for user_id in set(send_to):
        try:
            if markdown:
                bot.send_message(user_id, message, parse_mode=ParseMode.MARKDOWN)
            elif html:
                bot.send_message(user_id, message, parse_mode=ParseMode.HTML)
            else:
                bot.send_message(user_id, message)
        except TelegramError:
            pass  # ignore users who fail


def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def revert_buttons(buttons):
    res = ""
    for btn in buttons:
        if btn.same_line:
            res += "\n[{}](buttonurl://{}:same)".format(btn.name, btn.url)
        else:
            res += "\n[{}](buttonurl://{})".format(btn.name, btn.url)

    return res


def sendMessage(text: str, bot: Bot, update: Update):
    return bot.send_message(
        update.message.chat_id,
        reply_to_message_id=update.message.message_id,
        text=text,
        parse_mode=ParseMode.HTML,
    )


def build_keyboard_parser(bot, chat_id, buttons):
    keyb = []
    for btn in buttons:
        if btn.url == "{rules}":
            btn.url = "http://t.me/{}?start={}".format(bot.username, chat_id)
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def is_module_loaded(name):
    return name not in NO_LOAD
