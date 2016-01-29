import random

def get_or_create_session_id(request):
    # Set the session key string
    session_key = "{0}_id".format(request.session.session_key)
    # Fetch the session id using the session key string
    session_id = request.session.get(session_key)
    # If the session id was found by key
    if session_id:
        return session_id
    # Otherwise, generate a new session id
    else:
        request.session[session_key] = str(random.getrandbits(128))
        return request.session[session_key]