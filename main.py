import abc
import os
import logging
from typing import Callable, Any
from vk_api import VkApi
from vk_api.vk_api import VkApiMethod
from vk_api.longpoll import VkLongPoll, VkEventType, Event
from vk_api.keyboard import VkKeyboard, VkKeyboardColor, VkKeyboardButton
from vk_api.utils import get_random_id

from dotenv import load_dotenv
from storage.tiny import TinyStateStorage
from data.db import db
from data import models


storage = TinyStateStorage()


class State:
    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self) -> str:
        return self.name


class StateGroup:
    def __init__(self, states: list[State]) -> None:
        self.states = states
        self.current_state = 0

    def next(self):
        if self.current_state < len(self.states) - 1:
            self.current_state += 1

    def __call__(self) -> str:
        return self.states[self.current_state]()

    def __dict__(self) -> dict:
        return {"states": [state() for state in self.states]}


bot_states = StateGroup([State("menu"), State("task"), State("problem")])


def create_keyboard(buttons: list[str], one_time_: bool = True) -> VkKeyboard:

    keyboard = VkKeyboard(one_time=one_time_)
    for button in buttons:
        keyboard.add_button(button, color=VkKeyboardColor.PRIMARY)

    return keyboard


def send_message(
    vk, user_id: int, message: str = "", keyboard: VkKeyboard | None = None
) -> None:
    if keyboard:
        vk.messages.send(
            random_id=get_random_id(),
            user_id=user_id,
            message=message,
            keyboard=keyboard.get_keyboard(),
        )
    else:
        vk.messages.send(random_id=get_random_id(), user_id=user_id, message=message)


def process_event(vk, event: Event):

    if event.from_user and event.user_id:
        user_id = event.user_id
        state = storage.get_state(user_id)
        if event.text:
            event.text = event.text.lower()
        logging.debug(f"{user_id},{event.text},{state['name']}")
        match state["name"]:
            case "menu":
                if event.text == "задания":
                    avaliable_tasks = db.get_tasks()
                    storage.set_state(user_id, {"name": "task"})
                    send_message(
                        vk,
                        user_id,
                        "Доступные задания:",
                        create_keyboard([f"{task.ege_id}" for task in avaliable_tasks]),
                    )
                elif event.text == "статистика":
                    storage.set_state(user_id, {"name": "stats"})
                    send_message(
                        vk,
                        user_id,
                        "Статистика:",
                        create_keyboard(["Назад"]),
                    )
                else:
                    send_message(
                        vk,
                        user_id,
                        "Меню",
                        create_keyboard(
                            [
                                "Задания",
                                "Статистика",
                            ]
                        ),
                    )

            case "task":
                avaliable_tasks = db.get_tasks()
                tasks = {task.ege_id: task for task in avaliable_tasks}
                print(tasks)
                if event.text == "меню":
                    storage.set_state(user_id, {"name": "menu"})
                    send_message(
                        vk,
                        user_id,
                        "Меню",
                        create_keyboard(
                            [
                                "Задания",
                                "Статистика",
                            ]
                        ),
                    )
                elif not event.text.isdigit() or int(event.text) not in tasks.keys():
                    logging.error(
                        f"{user_id},{event.text},{state['name']},task_not_found"
                    )
                    send_message(
                        vk,
                        user_id,
                        "Нет такого задания, выбери задания из клавиатуры",
                        create_keyboard(
                            [f"{task.ege_id}" for task in avaliable_tasks] + ["Меню"]
                        ),
                    )
                else:
                    avaliable_problems = db.get_problems(tasks[int(event.text)].task_id)
                    storage.set_state(
                        user_id,
                        {
                            "name": "problem",
                            "task": tasks[int(event.text)].to_dict(),
                            "problems": [
                                problem.to_dict() for problem in avaliable_problems
                            ],
                        },
                    )
                    state = storage.get_state(user_id)
                    if len(state["problems"]) < 1:
                        logging.error(
                            f"{user_id},{event.text},{state['name']},problems_not_found"
                        )
                        send_message(
                            vk,
                            user_id,
                            "Проблемы не найдены",
                            create_keyboard(["Меню"]),
                        )
                    else:
                        send_message(
                            vk,
                            user_id,
                            f"{state['task']['description']}\n {state['problems'][0]['options']}",
                            create_keyboard(["к заданиям", "меню"]),
                        )

                if event.text == "назад":
                    storage.set_state(user_id, {"name": "menu"})
                    send_message(
                        vk,
                        user_id,
                        "Меню",
                        create_keyboard(
                            [
                                "Задания",
                                "Статистика",
                            ]
                        ),
                    )

            case "stats":
                if event.text == "назад":
                    storage.set_state(user_id, {"name": "menu"})
                    send_message(
                        vk,
                        user_id,
                        "Меню",
                        create_keyboard(
                            [
                                "Задания",
                                "Статистика",
                            ]
                        ),
                    )
            case "problem":
                state = storage.get_state(user_id)
                if event.text == "к заданиям":
                    storage.set_state(user_id, {"name": "task"})
                    avaliable_tasks = db.get_tasks()
                    send_message(
                        vk,
                        user_id,
                        "Доступные задания:",
                        create_keyboard([f"{task.ege_id}" for task in avaliable_tasks]),
                    )
                elif event.text == "меню":
                    storage.set_state(user_id, {"name": "menu"})
                    send_message(
                        vk,
                        user_id,
                        "Меню",
                        create_keyboard(
                            [
                                "Задания",
                                "Статистика",
                            ]
                        ),
                    )

                elif event.text == state["problems"][0]["correct_option"]:
                    send_message(vk, user_id, "Верно!")
                    state["problems"].pop(0)
                    storage.set_state(
                        user_id,
                        {
                            "name": "problem",
                            "task": state["task"],
                            "problems": state["problems"],
                        },
                    )
                    send_message(
                        vk,
                        user_id,
                        f"{state['task']['description']}\n {state['problems'][0]['options']}",
                        create_keyboard(["К заданиям", "меню"]),
                    )
                else:
                    send_message(vk, user_id, "Неверно!")
                    send_message(
                        vk,
                        user_id,
                        f"{state['task']['description']}\n {state['problems'][0]['options']}",
                        create_keyboard(["К заданиям", "меню"]),
                    )
                pass


def main():
    logging.basicConfig(level=logging.DEBUG)

    load_dotenv(".env")
    token = os.getenv("VK_TOKEN")
    if token is None:
        raise ValueError("VK_TOKEN not found")

    vk_session = VkApi(token=token)
    longpoll = VkLongPoll(vk_session)
    vk_api = vk_session.get_api()
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            process_event(vk_api, event)


if __name__ == "__main__":
    main()
