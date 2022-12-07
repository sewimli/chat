from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, run_js

import asyncio

chat_msgs = []
online_users = set()

MAX_MESSAGES_COUNT = 100

async def main():
    global chat_msgs

    put_markdown("Вітаю в онлайн чаті Титаренко Дарії")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input("Увійти в чат", required=True, placeholder="Ваше ім'я", validate=lambda n: "Такий нік вже використовуєьться." if n in online_users or n == '📢' else None)
    online_users.add(nickname)

    chat_msgs.append(('📢', f"`{nickname}` приєднався(-лась) до чату!"))
    msg_box.append(put_markdown(f"`{nickname}` приєднався(-лась) до чату!"))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    while True:
        data = await input_group("💭 Нове повідомлення", [
            input(placeholder="Текст повідомлення ...", name="msg"),
            actions(name="cmd", buttons=["Відіслати", {'label': "Вийти з чату", 'type':'cancel'}])
        ], validate=lambda m: ('msg', "Введіть текст повідомлення!") if m["cmd"] == "Надіслати" and not m["msg"] else None)

        if data is None:
            break
        msg_box.append(put_markdown(f"`{nickname}`: {data['msg']}"))
        chat_msgs.append((nickname, data['msg']))

    #exit chat
    refresh_task.close()

    online_users.remove(nickname)
    toast("Ви вийшли з чату!")
    msg_box.append(put_markdown(f"📢 Користувач `{nickname}` вийшов з чату."))
    chat_msgs.append(('📢', f"Користувач `{nickname}` вийшов з чату."))

    put_button(["Перезайти"], onclick=lambda btn: run_js('window.location.reload('))

async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)

        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

        #remove expired
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)

if __name__ == "__main__":
    start_server(main, debug=True, port=8080, cdn=False)