def normalize_status(status: str) -> str:
    return status.strip().lower()

def normalize_transaction(txn: dict) -> dict:
    txn["status"] = normalize_status(txn.get("status", ""))
    return txn