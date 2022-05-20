import os
import sys
import json


def get_config_json():
    """
    Opens and ensures config.json config file is valid
    If config.json does not exist, the program is terminated

    Returns: Dictionary with config key/values
    """
    if os.environ.get("QUEUE_USE_ENV"):
        CONFIG_FILE = "/data/config.json"
    else:
        CONFIG_FILE = "config.json"

    # Check if config file exists
    if not os.path.exists(CONFIG_FILE):
        print(f"{CONFIG_FILE} not found. Please add your secret token and ensure your bot is already in the desired server")
        sys.exit(1)

    # Read secrets.json file
    with open(CONFIG_FILE) as f:
        data = json.load(f)

    return data



class QueueConfig:
    """
    A storage class which holds all config values for QueueBot.
    On initialization, it does simple validation checks to see if
    the given config is properly configured. This object does not check
    if the values work for a given discord server - that must be verified
    after authentication has taken place.

    Paramters:
        config_obj: a dictionary with config options (see README.md for all options)
        from_env: True if config values come from environmental variables (for Docker)
        test_mode: set to True for unit test cases
    """
    def __init__(self, config_obj, from_env=False, test_mode=False):
        self.original_config = config_obj
        self.clean_config = self._validate_config(config_obj, from_env)
        self.FROM_ENV = from_env
        self.TEST_MODE = test_mode
        self.VERSION = "1.2.0"

        # TODO Default config attribtues so python knows the attribute exists...?

        # Each dictionary attribute becomes a constant field
        for key, val in self.clean_config.items():
            setattr(self, key.upper(), val)

    def _validate_config(self, config_obj, from_env):
        """
        Do basic error checking
        NOTE: This method terminates the program if a config option is invalid

        Parmeters:
            config_object: a dictionary with config options (see README for all options)
            from_env: True if config values come from environmental variables (for Docker)

        Returns: A clean dictionary (whitespace trimmed, etc.) with config options
        """

        # TODO Logger Level config option
        prefix = "QUEUE_" if from_env else ""
        error = {
            "SECRET_TOKEN": "You must update this field before the bot will connect",
            "TA_ROLES": "This field is required to allow administrators to remove users from the queue",
            "TEXT_LISTENS": "You must update this field to allow the bot to read commands",
            "VOICE_WAITING": "You must define which voice channel is a waiting room when you have CHECK_VOICE_WAITING enabled",
            "VOICE_OFFICES": "You must define Office Hour(s) voice channels when you have ALERT_ON_FIRST_JOIN is enabled",
            "TEXT_ALERT": "You must define an alerts channel so the bot can send you notification message"
        }

        config_clean = {
            "SECRET_TOKEN": config_obj["SECRET_TOKEN"].strip(),
            "TA_ROLES": [r.strip() for r in config_obj["TA_ROLES"] if r],
            "CHECK_VOICE_WAITING": config_obj["CHECK_VOICE_WAITING"].strip().lower() == "true",
            "TEXT_LISTENS": [c.strip().lstrip("#") for c in config_obj["TEXT_LISTENS"] if c],
            "ALERT_ON_FIRST_JOIN": config_obj["ALERT_ON_FIRST_JOIN"].strip().lower() == "true",
        }

        if config_clean["ALERT_ON_FIRST_JOIN"]:
            config_clean["TEXT_ALERT"] = config_obj["TEXT_ALERT"].strip()

        if config_clean["CHECK_VOICE_WAITING"]:
            config_clean["VOICE_WAITING"] = config_obj["VOICE_WAITING"].strip()

        if config_clean["ALERT_ON_FIRST_JOIN"]:
            config_clean["VOICE_OFFICES"] = [v.strip()
                                             for v in config_obj["VOICE_OFFICES"] if v]

        if config_clean["SECRET_TOKEN"] == "YOUR_SECRET_TOKEN_HERE":
            print(prefix + "SECRET_TOKEN is empty!")
            print(error["SECRET_TOKEN"])
            sys.exit(1)

        # Simple error checking. Make sure non-booleans are nonempty
        for key, val in config_clean.items():
            if isinstance(val, bool):
                continue
            if len(val) == 0:
                print(prefix + key, "is empty!")
                print(error[key])
                sys.exit(1)

        if config_clean["CHECK_VOICE_WAITING"] and config_clean["ALERT_ON_FIRST_JOIN"] and \
                        config_clean["VOICE_WAITING"] in config_clean["VOICE_OFFICES"]:
            print(config_clean["VOICE_WAITING"], "can be either the waiting room or an office room not both!")
            sys.exit(1)

        return config_clean

    def copy(self):
        """
        Return a clone of the QueueBot config
        """
        return QueueConfig(self.original_config.copy(),
                           from_env=self.FROM_ENV, test_mode=self.TEST_MODE)

    def __str__(self):
        retval = []
        banner_width = 60
        prefix = "QUEUE_" if self.FROM_ENV else ""
        retval.append('=' * banner_width + "\n")
        retval.append(f"VERSION: {self.VERSION}\n")
        for key, val in self.clean_config.items():
            if key == "SECRET_TOKEN":
                val = '*' * 40
            retval.append(f"{prefix}{key}: {val}\n")
        retval.append('=' * banner_width + "\n")

        return "".join(retval)
