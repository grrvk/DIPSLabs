import hashlib
import logging
import time

from src.utils import find_contract


class HTLC:
    def __init__(self, balances, balance_lock, logger: logging.Logger) -> None:
        self._balances = balances
        self._lock = balance_lock
        self._log = logger

    def lock(self, blockchain, sender: str, receiver: str, amount: float,
             hashlock: str, timelock_seconds: float) -> tuple[str, float]:
        """
            Lock funds. Write contract to blockchain under its txid.
        """

        timelock = time.time() + timelock_seconds
        raw = f"{sender}{receiver}{amount}{hashlock}{timelock}"
        txid = hashlib.sha256(raw.encode()).hexdigest()

        with self._lock:
            if self._balances[sender] < amount:
                self._log.error(f"Insufficient balance: {sender} has {self._balances[sender]}, needs {amount}")
                raise ValueError(f"Insufficient balance for {sender}")
            self._balances[sender] = self._balances[sender] - amount

        record = {
            "txid": txid,
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "hashlock": hashlock,
            "timelock": timelock,
            "status": "locked",
            "preimage": None,
        }
        blockchain[txid] = record
        return txid, timelock

    def redeem(self, blockchain, hashlock: str, preimage: str) -> bool:
        """
            Claim funds. Scan chain for matching hashlock, verify preimage, transfer funds.
        """
        contract = find_contract(blockchain, hashlock)
        if contract is None:
            self._log.error("redeem: contract not found")
            return False
        if contract["status"] != "locked":
            self._log.warning(f"redeem: contract status is {contract['status']}")
            return False
        if hashlib.sha256(preimage.encode()).hexdigest() != hashlock:
            self._log.error("redeem: preimage does not match hashlock")
            return False
        if time.time() >= contract["timelock"]:
            self._log.error("redeem: timelock expired")
            return False

        with self._lock:
            self._balances[contract["receiver"]] = self._balances[contract["receiver"]] + contract["amount"]

        contract["status"] = "redeemed"
        contract["preimage"] = preimage
        blockchain[contract["txid"]] = contract
        return True

    def refund(self, blockchain, hashlock: str) -> bool:
        """
            Return funds. Scan chain for matching hashlock, verify timelock expired.
        """
        contract = find_contract(blockchain, hashlock)
        if contract is None:
            self._log.error("refund: contract not found")
            return False
        if contract["status"] != "locked":
            self._log.warning(f"refund: contract status is {contract['status']}")
            return False
        if time.time() < contract["timelock"]:
            self._log.warning("refund: timelock not yet expired")
            return False

        with self._lock:
            self._balances[contract["sender"]] = self._balances[contract["sender"]] + contract["amount"]

        contract["status"] = "refunded"
        blockchain[contract["txid"]] = contract
        return True