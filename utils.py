import logging

def validate_transaction(txn: dict, seen_ids: set = None) -> bool:
    """
    Validates a transaction dictionary to ensure it has the required fields,
    correct data types, and no duplicate IDs.

    Args:
        txn (dict): The transaction to validate.
        seen_ids (set, optional): A set to track duplicate transaction IDs.

    Returns:
        bool: True if the transaction is valid, False otherwise.
    """
    required_fields = {
        "transaction_id": str,
        "status": str,
        "ISIN": str,
    }

    for field, expected_type in required_fields.items():
        if field not in txn or not isinstance(txn[field], expected_type):
            logging.warning(f"Validation failed for transaction: {txn}. Missing or invalid field: {field}")
            return False

    # Check for duplicate transaction IDs
    if seen_ids is not None:
        if txn["transaction_id"] in seen_ids:
            logging.warning(f"Duplicate transaction ID detected: {txn['transaction_id']}")
            return False
        seen_ids.add(txn["transaction_id"])

    return True


def normalize_status(status: str) -> str:
    """
    Normalize the status field by converting it to lowercase and stripping whitespace.

    Args:
        status (str): The status string to normalize.

    Returns:
        str: The normalized status string.
    """
    return status.strip().lower() if isinstance(status, str) else status


def normalize_field(value: str) -> str:
    """
    Normalize a generic field by stripping whitespace and converting to lowercase.

    Args:
        value (str): The field value to normalize.

    Returns:
        str: The normalized field value.
    """
    return value.strip().lower() if isinstance(value, str) else value


def normalize_transaction(txn: dict) -> dict:
    """
    Normalize fields in a transaction dictionary.

    Args:
        txn (dict): The transaction to normalize.

    Returns:
        dict: The normalized transaction.
    """
    if "status" in txn:
        txn["status"] = normalize_status(txn["status"])
        logging.info(f"Normalized status: {txn['status']}")
    if "asset_type" in txn:
        txn["asset_type"] = normalize_field(txn["asset_type"])
        logging.info(f"Normalized asset_type: {txn['asset_type']}")
    if "counterparty" in txn:
        txn["counterparty"] = normalize_field(txn["counterparty"])
        logging.info(f"Normalized counterparty: {txn['counterparty']}")
    return txn