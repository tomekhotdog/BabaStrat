from babaApp.models import Strategy, User


# Determines whether a trade can be execute for a user with
# respect to available funds and additional considerations
def can_execute_trade(user, strategy, quantity, direction, price_per_unit):
    if quantity <= 0:
        return False

    return True
