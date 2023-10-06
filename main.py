import datetime
import logging
import os
import sys
import argparse

from dotenv import load_dotenv
from vk_api import VkApi
from vk_api.keyboard import VkKeyboard
from vk_api.keyboard import VkKeyboardColor
from vk_api.longpoll import Event
from vk_api.longpoll import VkEventType
from vk_api.longpoll import VkLongPoll
from vk_api.utils import get_random_id

from data.db import db
from storage.tiny import TinyStateStorage

logger = logging.getLogger(__name__)


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


def process_event(vk, event: Event, storage):
    if event.from_user and event.user_id:
        user_id = event.user_id
        state = storage.get_state(user_id)
        logger.debug(f"event_info,{user_id},{event.text},{state['name']}")
        if event.text:
            event.text = event.text.lower()
        match state["name"]:
            case "menu":
                if event.text == "задания":
                    available_tasks = db.get_tasks()
                    storage.set_state(user_id, {"name": "task"})
                    logger.info(
                        f"menu_task,{user_id},{event.text},{state['name']},transition"
                    )
                    send_message(
                        vk,
                        user_id,
                        "Доступные задания:",
                        create_keyboard([f"{task.ege_id}" for task in available_tasks]),
                    )
                elif event.text == "статистика":
                    storage.set_state(user_id, {"name": "stats"})
                    logger.info(
                        f"menu_stats,{user_id},{event.text},{state['name']},transition"
                    )
                    send_message(vk, user_id, "Статистика:", create_keyboard(["Назад"]))
                else:
                    logger.info(
                        f"menu_buttons,{user_id},{event.text},{state['name']},transition"
                    )
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
                available_tasks = db.get_tasks()
                tasks = {task.ege_id: task for task in available_tasks}
                if event.text == "меню":
                    logger.info(
                        f"task_menu,{user_id},{event.text},{state['name']},transition"
                    )
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
                    logger.error(
                        f"menu_task_id,{user_id},{event.text},{state['name']},task_not_found"
                    )
                    send_message(
                        vk,
                        user_id,
                        "Нет такого задания, выбери задания из клавиатуры",
                        create_keyboard(
                            [f"{task.ege_id}" for task in available_tasks] + ["Меню"]
                        ),
                    )
                else:
                    logger.info(
                        f"menu_task_id,{user_id},{event.text},{state['name']},task_found"
                    )
                    available_problems = db.get_problems(tasks[int(event.text)].task_id)  # type: ignore
                    storage.set_state(
                        user_id,
                        {
                            "name": "problem",
                            "task": tasks[int(event.text)].to_dict(),  # type: ignore
                            "problems": [
                                problem.to_dict() for problem in available_problems  # type: ignore
                            ],
                        },
                    )
                    state = storage.get_state(user_id)
                    if len(state["problems"]) < 1:
                        logger.error(
                            f"menu_task_problems,{user_id},{event.text},{state['name']},problems_not_found"
                        )
                        send_message(
                            vk,
                            user_id,
                            "Проблемы не найдены",
                            create_keyboard(["Меню"]),
                        )
                    else:
                        logger.info(
                            f"menu_task_problems,{user_id},{event.text},{state['name']},problems_found"
                        )
                        options = "\n".join(state["problems"][0]["options"].split(";"))
                        send_message(
                            vk,
                            user_id,
                            f"{state['task']['description']}\n\n{options}",
                            create_keyboard(["к заданиям", "меню"]),
                        )
                if event.text == "назад":
                    logger.info(
                        f"menu_task_menu,{user_id},{event.text},{state['name']},transition"
                    )
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
                    logger.info(
                        f"menu_stats_menu,{user_id},{event.text},{state['name']},transition"
                    )
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
                    logger.info(
                        f"menu_task_problem_task,{user_id},{event.text},{state['name']},transition"
                    )
                    storage.set_state(user_id, {"name": "task"})
                    available_tasks = db.get_tasks()
                    keyboard = create_keyboard(
                        [f"{task.ege_id}" for task in available_tasks]
                    )
                    send_message(vk, user_id, "Доступные задания:", keyboard)
                elif event.text == "меню":
                    logger.info(
                        f"menu_task_problem_menu,{user_id},{event.text},{state['name']},transition"
                    )
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
                    logger.info(
                        f"menu_task_problem,{user_id},{event.text},{state['name']},correct_answer"
                    )
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
                    logger.info(
                        f"menu_task_problem,{user_id},{event.text},{state['name']},incorrect_answer"
                    )
                    send_message(vk, user_id, "Неверно!")
                    keyboard = create_keyboard(["К заданиям", "меню"])
                    send_message(
                        vk,
                        user_id,
                        f"{state['task']['description']}\n {state['problems'][0]['options']}",
                        keyboard,
                    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--db", type=str, default="sqlite:///db.sqlite3")
    parser.add_argument("--debug", type=str, default=False)

    args = parser.parse_args()

    storage = TinyStateStorage()

    logger.info("Starting")

    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.addHandler(logging.StreamHandler(sys.stdout))

    token = os.getenv("VK_TOKEN")
    if token is None:
        raise ValueError("VK_TOKEN not found")

    events = None
    if args.debug:
        events = []

    vk_session = VkApi(token=token)

    longpoll = VkLongPoll(vk_session)
    vk_api = vk_session.get_api()
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                if events and args.debug:
                    events.append(event)
                process_event(vk_api, event, storage)
    except KeyboardInterrupt:
        if events and args.debug:
            import pickle

            with open("test-events.pickle", "wb") as f:
                pickle.dump(events, f)
        logger.info("Keyboard interrupt")
    finally:
        logger.info("Exiting")


if __name__ == "__main__":
    main()
