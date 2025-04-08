import json
from datetime import datetime

def is_subscribed(user_id: int) -> bool:
    try:
        with open("subscribers.json", "r") as file:
            subscribers = json.load(file)

        user_id_str = str(user_id)
        if user_id_str in subscribers:
            expiry_str = subscribers[user_id_str].get("expiry")
            if not expiry_str:
                return False
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
            return datetime.now() < expiry_date
        else:
            return False
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False
