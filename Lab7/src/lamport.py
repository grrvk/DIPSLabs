import hashlib


class LamportOTPChain:
    def __init__(self, seed: str, length: int) -> None:
        self._chain: list[str] = [seed]
        for _ in range(length):
            self._chain.append(hashlib.sha256(self._chain[-1].encode()).hexdigest())
        self._length = length
        self._pointer = length

    @property
    def public_hash(self) -> str:
        return self._chain[self._length]

    def next_otp(self) -> str | None:
        if self._pointer <= 0:
            return None
        otp = self._chain[self._pointer - 1]
        self._pointer -= 1
        return otp

    def get_otp_at(self, index: int) -> str:
        return self._chain[index]


def verify_otp(stored_hash: str, otp: str) -> bool:
    return hashlib.sha256(otp.encode()).hexdigest() == stored_hash
