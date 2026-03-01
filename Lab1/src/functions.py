import os

import multiprocessing as mp
from multiprocessing.connection import Connection

from src.models import UID, ProcessNode
from typing import Optional, List
import random


def initialize_node(
        clockwise_conn: Connection,
        counterclockwise_conn: Connection,
        pid: Optional[int] = None
    ):
    uid = os.getpid() if pid is None else pid
    node = ProcessNode(UID(uid), clockwise_conn, counterclockwise_conn)
    node.run()

def create_ring(
        n: int,
    ):
    if n < 2:
        raise ValueError("Ring must have at least 2 process nodes")

    pipes = [mp.Pipe(duplex=True) for _ in range(n)]

    processes = []
    pids = [None for _ in range(n)]
    # pids = random.sample(range(100, n*100), n)
    for i in range(n):
        clockwise_conn = pipes[i][0]
        counterclockwise_conn = pipes[i-1][1]

        p = mp.Process(target=initialize_node, args=(clockwise_conn, counterclockwise_conn, pids[i]))
        processes.append(p)
        p.start()

    created_processes =  ", ".join([str(p.pid) for p in processes]) if pids[0] is None else ", ".join([str(p) for p in pids])
    print(f'created processes with uids: {created_processes}')

    for p in processes:
        p.join()