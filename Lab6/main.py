from multiprocessing import Manager, Process

from src.parties import alice_process, bob_process, charlie_process

SIMULATE_ATTACK = False


def main() -> None:
    with Manager() as manager:
        blockchain_A = manager.dict()
        blockchain_B = manager.dict()
        blockchain_C = manager.dict()

        balances = manager.dict({
            "Alice":   100.0,
            "Bob":     100.0,
            "Charlie": 100.0,
        })
        balance_lock = manager.Lock()

        hashlock_shared = manager.Value(str, "")

        events = {
            "htlc1_created": manager.Event(),
            "htlc2_created": manager.Event(),
            "htlc3_created": manager.Event(),
        }

        args = (blockchain_A, blockchain_B, blockchain_C, balances, balance_lock, events, hashlock_shared)
        processes = [
            Process(target=alice_process,   args=(*args, SIMULATE_ATTACK)),
            Process(target=bob_process,     args=(*args, SIMULATE_ATTACK)),
            Process(target=charlie_process, args=(*args, SIMULATE_ATTACK)),
        ]

        for p in processes:
            p.start()
        for p in processes:
            p.join()

        print("\nFinal Balances")
        for party in ("Alice", "Bob", "Charlie"):
            print(f"  {party:<8}: {balances[party]:.1f}")

        print("\nBlockchain A (Alice to Bob)")
        for txid, r in blockchain_A.items():
            print(f"  txid={txid[:8]}:  {r['sender']} to {r['receiver']}, amount={r['amount']}, status={r['status']}")

        print("\nBlockchain B (Bob to Charlie)")
        for txid, r in blockchain_B.items():
            print(f"  txid={txid[:8]}:  {r['sender']} to {r['receiver']}, amount={r['amount']}, status={r['status']}")

        print("\nBlockchain C (Charlie to Alice)")
        for txid, r in blockchain_C.items():
            print(f"  txid={txid[:8]}:  {r['sender']} to {r['receiver']}, amount={r['amount']}, status={r['status']}")


if __name__ == "__main__":
    main()
