from vk_api.longpoll import VkEventType, Event


test_stats = [
    Event(raw=[4, 287, 17, 238864041, 1696446272, 'начать', {'title': ' ... '}, {}, 0]),
    Event(raw=[4, 289, 17, 238864041, 1696446347, 'Статистика', {'title': ' ... '}, {}, 0])
]


class FakeLongPoll:
    """
    class for testing purposes:
        provides testing data in format of vk_api.VkLongPoll
    """

    def __init__(self, test_case_name: str):
        # create different event of differemt test_case_names
        self.events = list()
        self.current_event = 0
        if test_case_name == "stats":
            self.events = test_stats

    def listen(self):
        yield self.events[self.current_event]
        self.current_event += 1
