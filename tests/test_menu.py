from . import longpoll, vkapi

from main import process_event
from vk_api.longpoll import VkLongPoll, VkEventType, Event
from storage.tiny import TinyStateStorage


def test_stats():
    poll = longpoll.FakeLongPoll("stats")
    vk_api = vkapi.FakeVkApi()
    fake_storage = TinyStateStorage(db_path="tests.json")
    for event in poll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            process_event(vk_api, event)
