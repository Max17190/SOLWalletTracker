from firebase_admin import db

def get_user_wallets(user_id):
    """
    Fetch all wallets for a specific user from Firebase.
    """
    try:
        user_ref = db.reference(f'users/{user_id}/wallets')
        return user_ref.get() or {}
    except Exception as e:
        print(f"Error fetching wallets for user {user_id}: {e}")
        return None


def save_user_wallet(user_id, wallet_name, wallet_address):
    """
    Save a new wallet for a user in Firebase.
    """
    try:
        user_ref = db.reference(f'users/{user_id}/wallets')
        user_wallets = user_ref.get() or {}
        user_wallets[wallet_name] = wallet_address
        user_ref.set(user_wallets)
        return True
    except Exception as e:
        print(f"Error saving wallet for user {user_id}: {e}")
        return False


def remove_user_wallet(user_id, wallet_name):
    """
    Remove a wallet by its name for a specific user in Firebase.
    """
    try:
        user_ref = db.reference(f'users/{user_id}/wallets')
        user_wallets = user_ref.get() or {}
        if wallet_name in user_wallets:
            del user_wallets[wallet_name]
            user_ref.set(user_wallets)
            return True
        return False
    except Exception as e:
        print(f"Error removing wallet for user {user_id}: {e}")
        return False
