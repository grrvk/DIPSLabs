import hashlib
import os
import time

from src.htlc import HTLC
from src.logger import setup_logger
from src.utils import find_contract, watch_for_preimage

HTLC1_AMOUNT = 10.0   # Alice 2 Bob
HTLC2_AMOUNT = 20.0   # Bob 2 Charlie
HTLC3_AMOUNT = 15.0   # Charlie 2 Alice


def _audit_contract(contract: dict, expected_receiver: str, expected_amount: float,
                    log, chain_name: str) -> bool:
    if contract["receiver"] != expected_receiver:
        log.error(f"Audit failed on {chain_name}: receiver={contract['receiver']!r}, expected {expected_receiver!r}")
        return False
    if contract["amount"] != expected_amount:
        log.error(f"Audit failed on {chain_name}: amount={contract['amount']}, expected {expected_amount}")
        return False
    if time.time() + 3 >= contract["timelock"]:
        log.error(f"Audit failed on {chain_name}: timelock too close or already expired")
        return False
    return True


def alice_process(blockchain_A, blockchain_B, blockchain_C, balances, balance_lock,
                  events: dict, hashlock_shared, simulate_attack: bool) -> None:
    log = setup_logger("Alice")

    preimage = os.urandom(16).hex()
    hashlock = hashlib.sha256(preimage.encode()).hexdigest()
    hashlock_shared.value = hashlock
    log.info(f"Generated hashlock: {hashlock[:8]}. Preimage kept secret.")

    htlc = HTLC(balances, balance_lock, log)
    txid, _ = htlc.lock(blockchain_A, "Alice", "Bob", HTLC1_AMOUNT, hashlock, timelock_seconds=60)
    log.info(f"Locked HTLC on blockchain_A: txid={txid[:8]}..., {HTLC1_AMOUNT:.0f} coins to Bob, deadline in 60s, balance: {balances['Alice']:.1f}")
    events["htlc1_created"].set()

    if not events["htlc3_created"].wait(timeout=30):
        log.error("Swap aborted: HTLC_3 was never created within 30s — possible attack by Bob or Charlie.")
        log.info("Waiting for HTLC_1 timelock to expire to reclaim funds.")
        while not htlc.refund(blockchain_A, hashlock):
            time.sleep(10)
        log.info(f"Refunded HTLC_1. Balance: {balances['Alice']:.1f}")
        return

    log.info(f"Scanning blockchain_C for hashlock {hashlock[:8]}...")
    contract3 = find_contract(blockchain_C, hashlock)
    if contract3 is None:
        log.error("Contract not found on blockchain_C. Aborting.")
        return
    log.info(f"Found contract txid={contract3['txid'][:8]}. Auditing.")
    if not _audit_contract(contract3, "Alice", HTLC3_AMOUNT, log, "blockchain_C"):
        log.error("Audit failed on blockchain_C: aborting")
        return

    log.info("Audit passed. Redeeming. Publishing preimage to blockchain_C")
    htlc.redeem(blockchain_C, hashlock, preimage)
    log.info(f"Redeemed {HTLC3_AMOUNT:.0f} coins from Charlie")
    log.info(f"Swap complete. Balance: {balances['Alice']:.1f}")


def bob_process(blockchain_A, blockchain_B, blockchain_C, balances, balance_lock,
                events: dict, hashlock_shared, simulate_attack: bool) -> None:
    log = setup_logger("Bob")
    log.info("Started. Waiting for event_htlc1_created.")
    events["htlc1_created"].wait()

    hashlock: str = hashlock_shared.value
    contract1 = find_contract(blockchain_A, hashlock)
    if contract1 is None:
        log.error("Contract not found on blockchain_A. Aborting.")
        return
    log.info(f"Found contract txid={contract1['txid'][:8]}. Auditing.")
    if not _audit_contract(contract1, "Bob", HTLC1_AMOUNT, log, "blockchain_A"):
        log.error("Audit failed on blockchain_A: aborting")
        return

    htlc = HTLC(balances, balance_lock, log)

    if simulate_attack:
        fake_hashlock = hashlib.sha256(b"tampered").hexdigest()
        log.warning(f"[ATTACK] Locking HTLC_2 with tampered hashlock: {fake_hashlock[:8]} instead of {hashlock[:8]}.")
        lock_hashlock = fake_hashlock
    else:
        lock_hashlock = hashlock

    txid, tl2 = htlc.lock(blockchain_B, "Bob", "Charlie", HTLC2_AMOUNT, lock_hashlock, timelock_seconds=30)
    log.info(f"Audit passed. Locking HTLC on blockchain_B: txid={txid[:8]}, "
             f"{HTLC2_AMOUNT:.0f} coins to Charlie, deadline in 30s, balance: {balances['Bob']:.1f}")
    events["htlc2_created"].set()

    preimage = watch_for_preimage(blockchain_C, hashlock, deadline=tl2)
    if preimage is None:
        log.warning("Deadline passed. Triggering refund on blockchain_B.")
        htlc.refund(blockchain_B, lock_hashlock)
        return

    log.info("Preimage detected on blockchain_C. Redeeming HTLC on blockchain_A.")
    htlc.redeem(blockchain_A, hashlock, preimage)
    log.info(f"Redeemed {HTLC1_AMOUNT:.0f} coins from Alice")
    log.info(f"Swap complete. Balance: {balances['Bob']:.1f}")


def charlie_process(blockchain_A, blockchain_B, blockchain_C, balances, balance_lock,
                    events: dict, hashlock_shared, simulate_attack: bool) -> None:
    log = setup_logger("Charlie")
    log.info("Started. Waiting for event_htlc2_created.")
    events["htlc2_created"].wait()

    hashlock: str = hashlock_shared.value
    contract2 = find_contract(blockchain_B, hashlock)
    if contract2 is None:
        log.error("Attack detected: no contract found on blockchain_B matching the known hashlock — Bob likely used a tampered hashlock. Aborting.")
        return
    log.info(f"Found contract txid={contract2['txid'][:8]}. Auditing.")
    if not _audit_contract(contract2, "Charlie", HTLC2_AMOUNT, log, "blockchain_B"):
        log.error("Audit failed on blockchain_B: aborting")
        return

    htlc = HTLC(balances, balance_lock, log)
    txid, tl3 = htlc.lock(blockchain_C, "Charlie", "Alice", HTLC3_AMOUNT, hashlock, timelock_seconds=15)
    log.info(f"Audit passed. Locking HTLC on blockchain_C: txid={txid[:8]}, "
             f"{HTLC3_AMOUNT:.0f} coins to Alice, deadline in 15s, balance: {balances['Charlie']:.1f}")
    events["htlc3_created"].set()

    preimage = watch_for_preimage(blockchain_C, hashlock, deadline=tl3)
    if preimage is None:
        log.warning("Deadline passed. Triggering refund on blockchain_C.")
        htlc.refund(blockchain_C, hashlock)
        return

    log.info("Preimage detected on blockchain_C. Redeeming HTLC on blockchain_B.")
    htlc.redeem(blockchain_B, hashlock, preimage)
    log.info(f"Redeemed {HTLC2_AMOUNT:.0f} coins from Bob")
    log.info(f"Swap complete. Balance: {balances['Charlie']:.1f}")