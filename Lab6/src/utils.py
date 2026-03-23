import time


def find_contract(blockchain, hashlock: str) -> dict | None:
    for txid, contract in blockchain.items():
        if contract["hashlock"] == hashlock:
            return dict(contract)
    return None


def watch_for_preimage(blockchain, hashlock: str, deadline: float) -> str | None:
    while time.time() < deadline:
        contract = find_contract(blockchain, hashlock)
        if contract and contract["preimage"] is not None:
            return contract["preimage"]
        time.sleep(0.2)
    return None