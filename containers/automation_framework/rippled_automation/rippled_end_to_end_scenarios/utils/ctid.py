def encodeCTID(ledger_seq, txn_index, network_id):
    if not isinstance(ledger_seq, int):
        raise ValueError("ledger_seq must be a number.")
    if ledger_seq > 0xFFFFFFF or ledger_seq < 0:
        raise ValueError("ledger_seq must not be greater than 268435455 or less than 0.")

    if not isinstance(txn_index, int):
        raise ValueError("txn_index must be a number.")
    if txn_index > 0xFFFF or txn_index < 0:
        raise ValueError("txn_index must not be greater than 65535 or less than 0.")

    if not isinstance(network_id, int):
        raise ValueError("network_id must be a number.")
    if network_id > 0xFFFF or network_id < 0:
        raise ValueError("network_id must not be greater than 65535 or less than 0.")

    ctid_value = ((0xC0000000 + ledger_seq) << 32) + (txn_index << 16) + network_id
    return format(ctid_value, 'x').upper()


def decodeCTID(ctid):
    if isinstance(ctid, str):
        if not ctid.isalnum():
            raise ValueError("ctid must be a hexadecimal string or BigInt")

        if len(ctid) != 16:
            raise ValueError("ctid must be exactly 16 nibbles and start with a C")

        ctid_value = int(ctid, 16)
    elif isinstance(ctid, int):
        ctid_value = ctid
    else:
        raise ValueError("ctid must be a hexadecimal string or BigInt")

    if ctid_value > 0xFFFFFFFFFFFFFFFF or ctid_value & 0xF000000000000000 != 0xC000000000000000:
        raise ValueError("ctid must be exactly 16 nibbles and start with a C")

    ledger_seq = (ctid_value >> 32) & 0xFFFFFFF
    txn_index = (ctid_value >> 16) & 0xFFFF
    network_id = ctid_value & 0xFFFF
    return {
        'ledger_seq': ledger_seq,
        'txn_index': txn_index,
        'network_id': network_id
    }
