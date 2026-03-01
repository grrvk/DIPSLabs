import time
from dataclasses import dataclass
from enum import Enum
from typing import NewType

from loguru import logger
from multiprocessing.connection import Connection, wait

UID = NewType("UID", int)

class MessageType(Enum):
    IN = 'in'
    OUT = 'out'


@dataclass
class DefaultMessage:
    uid: UID
    type: MessageType
    hop_count: int

@dataclass
class LeaderMessage:
    uid: UID

Message = DefaultMessage | LeaderMessage


class ProcessNode:
    def __init__(self, uid: UID, clockwise_conn: Connection, counterclockwise_conn: Connection):
        self.uid = uid
        self.phase = 0
        self.status = "Default"
        self.leader_uid = None
        self.rounds = 1

        self.cwc = clockwise_conn
        self.ccwc = counterclockwise_conn

        self.active = False
        self.leader_forwarded = False
        self.received_clockwise = False
        self.received_counterclockwise = False

        self.out_returned_cwc = False
        self.out_returned_ccwc = False

        self.total_clockwise_received = 0
        self.total_counterclockwise_received = 0

    def _send_message(self):
        message = DefaultMessage(self.uid, MessageType.OUT, 2**self.phase)
        self.cwc.send(message)
        self.ccwc.send(message)

    def _send_leader_message(self):
        leader_message = LeaderMessage(uid=self.uid)
        self.cwc.send(leader_message)

    def _receive_message(self, message: Message, connection: Connection):
        if self.leader_forwarded:
            return

        if connection is self.cwc:
            self.total_clockwise_received += 1
        else:
            self.total_counterclockwise_received += 1

        if isinstance(message, LeaderMessage):
            self.leader_uid = message.uid
            if message.uid != self.uid:
                print(f'Node [{self.uid}]: Leader is {self.leader_uid}')
                self.cwc.send(message)
                self.leader_forwarded = True
            return

        opposite_conn = self.ccwc if connection is self.cwc else self.cwc

        if message.type == MessageType.IN:
            self._handle_in_message(message, opposite_conn)
        elif message.type == MessageType.OUT:
            self._handle_out_message(message, connection, opposite_conn)

    def _handle_in_message(self, message: DefaultMessage, connection: Connection):

        if message.uid == self.uid:
            if connection is self.cwc:
                self.received_clockwise = True
            else:
                self.received_counterclockwise = True
            if self.received_clockwise and self.received_counterclockwise:
                self._advance_phase()
        else:
            direction = "clockwise" if connection is self.cwc else "counterclockwise"
            logger.debug(f"Node [{self.uid}] forwarding IN msg uid={message.uid} {direction}")
            connection.send(message)

    def _advance_phase(self):
        self.phase += 1
        self.received_clockwise = False
        self.received_counterclockwise = False
        self._send_message()

    def _handle_out_message(self, message: DefaultMessage, connection: Connection, opposite_conn: Connection):
        if message.uid == self.uid:
            if connection is self.cwc:
                self.out_returned_cwc = True
            else:
                self.out_returned_ccwc = True

            if self.out_returned_cwc and self.out_returned_ccwc:
                print(f'Node [{self.uid}]: I am the leader')
                self.status = "Leader"
                self.leader_uid = self.uid
                self._send_leader_message()
                self.leader_forwarded = True
            return

        if message.uid < self.uid:
            return

        if message.hop_count > 1:
            message.hop_count -= 1
            direction = "clockwise" if connection is self.cwc else "counterclockwise"
            logger.debug(f"Node [{self.uid}] forwarding OUT msg uid={message.uid} hops_left={message.hop_count} {direction}")
            connection.send(message)
        else:
            message.type = MessageType.IN
            direction = "clockwise" if opposite_conn is self.cwc else "counterclockwise"
            logger.debug(f"Node [{self.uid}] reversing msg uid={message.uid} to {direction}")
            opposite_conn.send(message)

    def print_statistics(self):
        logger.info(
            f"Node [{self.uid}] statistics: status={self.status}, "
            f"rounds_active={self.rounds}, "
            f"clockwise_received={self.total_clockwise_received}, "
            f"counterclockwise_received={self.total_counterclockwise_received}"
        )

    def run(self):
        self.active = True
        self._send_message()

        while self.active and not self.leader_forwarded:
            ready_conns = wait([self.cwc, self.ccwc], timeout=0.1)
            if not ready_conns:
                continue

            self.rounds += 1

            for conn in ready_conns:
                message = conn.recv()
                self._receive_message(message, conn)

        time.sleep(0.5)
        self.print_statistics()
        self.active = False


