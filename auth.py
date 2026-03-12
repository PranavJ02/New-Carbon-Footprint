from supabase_db import supabase

def register_user(name, email, username, password):

    data = {
        "name": name,
        "email": email,
        "username": username,
        "password": password
    }

    response = supabase.table("users").insert(data).execute()

    return True


def login_user(username, password):

    response = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()

    if response.data:
        return response.data[0]["id"]

    return None