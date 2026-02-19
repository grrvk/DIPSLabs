import os

import multiprocessing as mp
from multiprocessing.connection import Connection

from src.models import UID, ProcessNode


def initialize_node(
        clockwise_conn: Connection,
        counterclockwise_conn: Connection
    ):
    uid = os.getpid()
    node = ProcessNode(UID(uid), clockwise_conn, counterclockwise_conn)
    node.run()

def create_ring(
        n: int,
    ):
    if n < 2:
        raise ValueError("Ring must have at least 2 process nodes")

    pipes = [mp.Pipe(duplex=True) for _ in range(n)]

    processes = []
    for i in range(n):
        clockwise_conn = pipes[i][0]
        counterclockwise_conn = pipes[i-1][1]

        p = mp.Process(target=initialize_node, args=(clockwise_conn, counterclockwise_conn))
        processes.append(p)
        p.start()

    created_processes =  ", ".join([str(p.pid) for p in processes])
    print(f'created processes with uids: {created_processes}')

    for p in processes:
        p.join()