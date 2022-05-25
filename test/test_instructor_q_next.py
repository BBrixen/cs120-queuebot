import io
import time
import random
import unittest
import collections
from contextlib import redirect_stdout
from .utils import *

from src.queuebot import QueueBot

config = {
    "SECRET_TOKEN": "NOONEWILLEVERGUESSTHISSUPERSECRETSTRINGMWAHAHAHA",
    "CHECK_VOICE_WAITING": False,
    "ALERT_ON_FIRST_JOIN": False,

    "TEXT_ROLE_MANAGEMENT": "roles",

    "INSTRUCTOR_ROLES": ["NOT-APPLICABLE"],
    "CLASSES_CONFIG": {
        "120": {
            "TA_ROLES": ["UGTA"],
            "VOICE_WAITING": "120-waiting-room",
            "VOICE_OFFICES": ["Office Hours 1", "Office Hours 2"],
            "TEXT_LISTENS": ["join-queue"],
            "STUDENT_ROLE": "120 Student"
        },
        "346": {
            "TA_ROLES": ["UGTA"],
            "VOICE_WAITING": "346-waiting-room",
            "VOICE_OFFICES": ["Office Hours 1", "Office Hours 2"],
            "TEXT_LISTENS": ["join-queue"],
            "STUDENT_ROLE": "346 Student"
        }
    }
}

CLASS_LIST = {
    "120": {
        "KEY": "120",
        "TA_ROLES": ["UGTA"],
        "VOICE_WAITING":MockVoice("120-waiting-room"),
        "VOICE_OFFICES": [ MockVoice("Office Hours 1"), MockVoice("Office Hours 2"), MockVoice("Office Hours 3") ],
        "TEXT_LISTENS": [ MockChannel("120-join-queue") ],
        "STUDENT_ROLE": MockRole("120 Student"),
        "QUEUE": collections.deque()
    },
    "346": {
        "KEY": "346",
        "TA_ROLES": ["UGTA"],
        "VOICE_WAITING":MockVoice("346-waiting-room"),
        "VOICE_OFFICES": [ MockVoice("Office Hours 1"), MockVoice("Office Hours 2"), MockVoice("Office Hours 3") ],
        "TEXT_LISTENS": [ MockChannel("346-join-queue") ],
        "STUDENT_ROLE": MockRole("120 Student"),
        "QUEUE": collections.deque()
    }
}

JOIN_120 = CLASS_LIST["120"]["TEXT_LISTENS"][0]
JOIN_346 = CLASS_LIST["346"]["TEXT_LISTENS"][0]
INSTRUCTOR_DMS = MockDMChannel()

TEXT_LISTENS = {
    "120-join-queue": CLASS_LIST["120"],
    "346-join-queue": CLASS_LIST["346"]
}

# TODO Comment each test case

russ = MockAuthor("Russ", None, ["UGTA"])

class QueueTest(unittest.TestCase):
    def setUp(self):
        random.seed(SEED)
        self.config = config.copy()
        self.bot = QueueBot(self.config, None)
        self.bot._testing = True
        self.bot._logger = MockLogger()
        self.bot._class_list = CLASS_LIST
        self.bot._all_text_listens = TEXT_LISTENS

    def test_empty(self):
        self.assertEqual(len(CLASS_LIST["346"]["QUEUE"]), 0)
        self.assertEqual(len(CLASS_LIST["120"]["QUEUE"]), 0)

        message = MockMessage("!q next", russ, INSTRUCTOR_DMS)
        with io.StringIO() as buf, redirect_stdout(buf):
            run(self.bot.queue_command_instructor(message))
            self.assertEqual(buf.getvalue().strip(), "SEND DM: All queues are empty")

    def test_simple_next(self):
        students = get_n_rand(ALL_STUDENTS, 8)
        students_120 = students[:4]
        students_346 = students[4:]

        message = MockMessage("!q join-inperson", students_346[0], JOIN_346)
        with io.StringIO() as buf, redirect_stdout(buf):
            run(self.bot._queue_command(message))
            self.assertEqual(len(CLASS_LIST["346"]["QUEUE"]), 1)

        # TODO Make a way to test student joins *without* having to sleep
        time.sleep(5)

        message = MockMessage("!q join-inperson", students_120[0], JOIN_120)
        with io.StringIO() as buf, redirect_stdout(buf):
            run(self.bot._queue_command(message))
            self.assertEqual(len(CLASS_LIST["120"]["QUEUE"]), 1)

        message = MockMessage("!q list", russ, INSTRUCTOR_DMS)
        with io.StringIO() as buf, redirect_stdout(buf):
            run(self.bot.queue_command_instructor(message))
            self.assertEqual(buf.getvalue().strip(),
                f"SEND DM: None embed.title='Queue List', embed.description=Total in queue: 2, fields=[EmbedProxy(inline=False, name='Next 10 people:', value='**1.** (346) {students_346[0].get_mention()} __*(in person)*__\\n**2.** (120) {students_120[0].get_mention()} __*(in person)*__')]")

        message = MockMessage("!q next", russ, INSTRUCTOR_DMS)
        with io.StringIO() as buf, redirect_stdout(buf):
            run(self.bot.queue_command_instructor(message))
            self.assertTrue(buf.getvalue().lstrip().startswith(f"SEND DM: The next person is **346** __[]__ ({students_346[0].get_mention()})__*(in person)*__"))
            self.assertEqual(len(CLASS_LIST["346"]["QUEUE"]), 0)
            self.assertEqual(len(CLASS_LIST["120"]["QUEUE"]), 1)

        message = MockMessage("!q next", russ, INSTRUCTOR_DMS)
        with io.StringIO() as buf, redirect_stdout(buf):
            run(self.bot.queue_command_instructor(message))
            self.assertTrue(buf.getvalue().lstrip().startswith(f"SEND DM: The next person is **120** __[]__ ({students_120[0].get_mention()})__*(in person)*__"))
            self.assertEqual(len(CLASS_LIST["346"]["QUEUE"]), 0)
            self.assertEqual(len(CLASS_LIST["120"]["QUEUE"]), 0)
