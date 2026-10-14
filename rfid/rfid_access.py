"""
rfid_access.py
==============
RFID door access system (interview practice task).

Rules (from the task):
  - One main door; each door knows its previous door and its next doors.
  - A tag opens a door only if that tag already opened the previous door
    or this same door. The main door has no previous door.
  - Each employee can open at most one door every 2 seconds.

Decisions confirmed during the session:
  - A swipe exactly 2.000s after the last open is allowed.
  - Only a real open starts the 2-second wait (a denied swipe does not).
"""

import logging
import time

logger = logging.getLogger(__name__)

MIN_SECONDS_BETWEEN_OPENS = 2.0


class Door:
    def __init__(self, door_id):
        self.door_id = door_id
        self.previous = None
        self.next_doors = []

    def add_next(self, door):
        door.previous = self
        self.next_doors.append(door)


class AccessSystem:
    def __init__(self, doors, clock=time.monotonic):
        self._doors = {door.door_id: door for door in doors}
        self._clock = clock
        self._opened = {}     # tag_id -> set of door_ids this tag opened
        self._last_open = {}  # tag_id -> time of this tag's last real open

    def swipe(self, tag_id, door_id):
        """Return True if the door opens for this tag, False if denied.
        Raises ValueError for an unknown door_id."""
        if door_id not in self._doors:
            raise ValueError(f"Unknown door: {door_id}")
        if not tag_id:
            logger.warning("Access denied: empty tag at door %s", door_id)
            return False

        door = self._doors[door_id]
        opened = self._opened.get(tag_id, set())
        now = self._clock()

        last = self._last_open.get(tag_id)
        if last is not None and now - last < MIN_SECONDS_BETWEEN_OPENS:
            logger.warning("Access denied: tag %s at door %s, under %ss since last open",
                           tag_id, door_id, MIN_SECONDS_BETWEEN_OPENS)
            return False

        is_main = door.previous is None
        if not (is_main or door.previous.door_id in opened or door_id in opened):
            logger.warning("Access denied: tag %s at door %s, previous door %s not opened",
                           tag_id, door_id, door.previous.door_id)
            return False

        self._opened.setdefault(tag_id, set()).add(door_id)
        self._last_open[tag_id] = now
        return True
