def validate_transaction(txn: dict) -> bool:
    required_fields = ["transaction_id", "status", "ISIN"]
    return all(field in txn for field in required_fields)

def validate_transactions(transactions: list) -> list:
    valid_transactions = []
    for txn in transactions:
        if validate_transaction(txn):
            valid_transactions.append(txn)
        else:
            logging.warning(f"Invalid transaction: {txn}")
    return valid_transactions