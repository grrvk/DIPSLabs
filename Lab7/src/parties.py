import os

from src.lamport import LamportOTPChain, verify_otp
from src.logger import setup_logger

N_ROUNDS = 5


def alice_process(auth_state, submissions, alice_q, events: dict,
                  attack_type: str, simulate_attack: bool) -> None:
    log = setup_logger("Alice")

    seed = os.urandom(16).hex()
    chain = LamportOTPChain(seed, N_ROUNDS)

    log.info(f"Generated OTP chain (length={N_ROUNDS}). Public hash: {chain.public_hash[:8]}...")
    auth_state["stored_hash"] = chain.public_hash
    events["registered"].set()

    if simulate_attack and attack_type == "forgery":
        events["attacker_done"].wait()

    for i in range(N_ROUNDS):
        otp = chain.next_otp()
        log.info(f"Round {i + 1}/{N_ROUNDS}: submitting OTP {otp[:8]}...")
        submissions.put({"otp": otp, "sender": "Alice"})

        result = alice_q.get()
        if result["accepted"]:
            log.info(f"Round {i + 1}/{N_ROUNDS}: ACCEPTED.")
        else:
            log.error(f"Round {i + 1}/{N_ROUNDS}: REJECTED! Aborting.")
            return

        if simulate_attack and attack_type == "replay" and i == 0:
            auth_state["captured_otp"] = otp
            events["round1_done"].set()
            events["attacker_done"].wait()

    log.info(f"All {N_ROUNDS} rounds passed. Chain exhausted.")
    events["auth_done"].set()

def bob_process(auth_state, submissions, alice_q, attacker_q, log_dict,
                events: dict, attack_type: str, simulate_attack: bool) -> None:
    log = setup_logger("Bob")
    log.info("Server started. Waiting for registration.")
    events["registered"].wait()
    log.info(f"Client registered. Stored hash: {auth_state['stored_hash'][:8]}...")

    total = N_ROUNDS + (1 if simulate_attack else 0)

    for i in range(total):
        entry   = submissions.get()
        otp     = entry["otp"]
        sender  = entry["sender"]
        stored  = auth_state["stored_hash"]

        accepted = verify_otp(stored, otp)
        result   = {"otp": otp, "sender": sender, "accepted": accepted}
        log_dict[i] = result

        if accepted:
            log.info(f"Submission {i + 1}: OTP from {sender} VALID — ratcheting stored hash.")
            auth_state["stored_hash"] = otp
        else:
            log.warning(f"Submission {i + 1}: OTP from {sender} INVALID — state unchanged.")

        if sender == "Alice":
            alice_q.put(result)
        else:
            attacker_q.put(result)

def eve_process(auth_state, submissions, attacker_q, events: dict) -> None:
    log = setup_logger("Eve")
    log.warning("[REPLAY] Waiting for Alice's round 1 to complete...")
    events["round1_done"].wait()

    w1 = auth_state["captured_otp"]
    log.warning(f"[REPLAY] Intercepted w1={w1[:8]}... — replaying it as round 2 OTP.")
    submissions.put({"otp": w1, "sender": "Eve"})

    result = attacker_q.get()
    events["attacker_done"].set()

    if result["accepted"]:
        log.error("[REPLAY] Attack SUCCEEDED — scheme is BROKEN!")
    else:
        log.info("[REPLAY] REJECTED — H(w1) != w1 — Bob's state unchanged.")

def charlie_process(auth_state, submissions, attacker_q, events: dict) -> None:
    log = setup_logger("Charlie")
    events["registered"].wait()

    fake = "fakehash" * 8
    log.warning(f"[FORGERY] Submitting forged OTP: {fake[:8]}... before Alice's round 1.")
    submissions.put({"otp": fake, "sender": "Charlie"})

    result = attacker_q.get()
    events["attacker_done"].set()

    if result["accepted"]:
        log.error("[FORGERY] Attack SUCCEEDED — scheme is BROKEN!")
    else:
        log.info("[FORGERY] REJECTED — H(forged) != stored_hash — Bob's state unchanged.")
