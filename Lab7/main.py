from multiprocessing import Manager, Process

from src.parties import (
    alice_process, bob_process, charlie_process, eve_process, N_ROUNDS,
)

SIMULATE_ATTACK = True
ATTACK_TYPE     = "forgery"


def main() -> None:
    with Manager() as manager:
        auth_state     = manager.dict()
        submissions    = manager.Queue()
        alice_q        = manager.Queue()
        attacker_q     = manager.Queue()
        log_dict       = manager.dict()

        events = {
            "registered":    manager.Event(),
            "auth_done":     manager.Event(),
            "round1_done":   manager.Event(),
            "attacker_done": manager.Event(),
        }

        alice_args = (auth_state, submissions, alice_q,        events, ATTACK_TYPE, SIMULATE_ATTACK)
        bob_args   = (auth_state, submissions, alice_q, attacker_q, log_dict, events, ATTACK_TYPE, SIMULATE_ATTACK)

        processes = [
            Process(target=alice_process, args=alice_args),
            Process(target=bob_process,   args=bob_args),
        ]

        if SIMULATE_ATTACK:
            if ATTACK_TYPE == "replay":
                processes.append(
                    Process(target=eve_process,
                            args=(auth_state, submissions, attacker_q, events))
                )
            elif ATTACK_TYPE == "forgery":
                processes.append(
                    Process(target=charlie_process,
                            args=(auth_state, submissions, attacker_q, events))
                )

        for p in processes:
            p.start()
        for p in processes:
            p.join()

        print("\nSubmission Log")
        for i in range(len(log_dict)):
            e      = log_dict[i]
            status = "ACCEPTED" if e["accepted"] else "REJECTED"
            print(f"  #{i + 1:>2}  sender={e['sender']:<8}  otp={e['otp'][:12]}...  {status}")

        print(f"\nFinal stored hash: {auth_state.get('stored_hash', '')[:12]}...")


if __name__ == "__main__":
    main()
