import time
import discord
import asyncio
import csv
from datetime import datetime, date

from enum import Enum


class CmdPrefix(Enum):
    """
    An Enum used to signify if the message is a success, warning, or error message
    This allows for extra formatting within the message to signify the importance.
    """
    SUCCESS = object()
    WARNING = object()
    ERROR = object()


class DiscordUser():
    """
    A simplified class to compare and store discord users
    This is used instead of the discord user object to facilitate testing

    Parameters:
        uuid: discord's unique identifier for a user
        name: username of a user
        discriminator: the four numbers that used after the username
                       for the external representation of a user
                       example: For "someuser#1234", 1234 is the discriminator
        nick: nickname of the user if it's different than the username. None otherwise
    """
    def __init__(self, uuid, name, discriminator, nick, inperson=False):
        self._uuid = uuid
        self._name = name
        self._discriminator = discriminator
        self._nick = nick
        self._inperson = inperson
        self._join_time = time.time()  # Unix Timestamp (assuming it's run on Linux)

    def get_uuid(self):
        """
        Get the UUID of the user

        Returns: A string containing the user's UUID
        """
        return self._uuid

    def get_mention(self):
        """
        Mention a user within a message

        Returns: A string that mentions the user
        """
        return f"<@{self._uuid}>"

    def get_tag(self):
        """
        Get a user's discord tag (how users externally add/mention friends)
        Format is username#NNNN where N is a number

        Returns: The user's discord tag
        """
        # External representation of a user
        return f"{self._name}#{self._discriminator}"

    def get_name(self):
        """
        Get the user's display name within the server

        Returns: The user's display name
        """
        if self._nick is None:
            return self._name

        return self._nick


    def is_inperson(self):
        """
        Check if a user is in person for office hours.
        If this returns False, the user is within the online queue.

        A boolean stating if the user is in person. True means in person
        while False means online.
        """
        return self._inperson

    def set_inperson(self, state):
        """
        Set the user's in person state

        Parameters:
            state: a boolean. True for in person False for online

        Returns: None
        """
        self._inperson = state

    def get_join_time(self):
        """
        Get the join time (as a unix timestamp via time.time()) from when the user was added to the queue.
        The time is computed upon object instantiaion.

        Return: join time unix timestamp (as a number)
        """
        return self._join_time

    def get_wait_time(self):
        """
        Compute the time delta between now and the user's join time

        Returns: the time the user waited in seconds
        """
        return time.time() - self._join_time

    def __str__(self):
        """
        Returns the discord internal representation of a user
        format: "<@USERID_HERE>"
        """
        return self.get_tag()

    def __repr__(self):
        return f"DiscordUser({self.uuid}, {self.name}, {self.discriminator}, {self.nick}, inperson={self.inperson})"

    def __eq__(self, other):
        """
        If other is DiscordUser ot discord.member.Member,
        it checks the uuids to see if they match.
        If it is not one of the two objects,
        it compares other with self.uuid

        Parameters:
            other: object to compare against

        Returns: True if objects have same uuid
        """

        if isinstance(other, DiscordUser):
            return self._uuid == other._uuid
        elif isinstance(other, discord.member.Member):
            return self._uuid == other.id

        return other == self._uuid


# log_session(user.get_mention(), self._join_times.get(user, None), None)
async def log_session(name, join_time, ta, command_type):
    lock = asyncio.Lock()

    # time related data
    current_time = datetime.now()
    current_date = current_time.strftime("%B %d, %Y")
    current_time = current_time.strftime("%H:%M")

    if join_time is None:
        join_time = "N/A"
        diff = "N/A"
    else:
        # time spent waiting
        join_time = join_time.strftime("%H:%M")
        t1 = datetime.strptime(join_time, "%H:%M")
        t2 = datetime.strptime(current_time, "%H:%M")
        diff = t2 - t1
        diff = str(diff)[:-3]

    if ta is None:
        ta = "N/A"

    async with lock:
        with open("logs/OH_logs.csv", 'a') as file:
            writer = csv.writer(file, delimiter='|')
            writer.writerow([name, current_date, join_time, ta, current_time, diff, command_type])
