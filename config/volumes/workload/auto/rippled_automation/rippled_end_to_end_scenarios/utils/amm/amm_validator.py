
def verify_auction_slot(account_id, amm_info, ignore_auction_slot=False):
    """Assert a specific account is present in an AMM object's auction slot"""
    if ignore_auction_slot:
        return
    slot_holder = amm_info['amm']['auction_slot']['account']
    msg = f"Account {account_id[:6]} is not in the auction slot!"
    assert account_id == slot_holder, msg
