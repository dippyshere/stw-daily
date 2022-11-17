# ---- CHECK FUNCTIONS ----


def check_upcoming_display_days(client, ctx, value):
    try:
        integer_value = int(value)
        if integer_value < 51 and integer_value > 0:
            return integer_value
        else:
            return False
    except:
        return False

boolean_string_representation = {'true': True, 't': True, '1': True,
                 'false': False, 'f': False, '0': False}

def check_bool(client, ctx, value):
    try:
        boolean_string_representation[value]
        return True
    except:
        return False


def check_localisation(client, ctx, value):
    if value.lower() in client.localisation:
        return client.localisation[value.lower()]
    else:
        return False


def sex_check(client, ctx, value):
    try:
        return str(value)
    except:
        return False
