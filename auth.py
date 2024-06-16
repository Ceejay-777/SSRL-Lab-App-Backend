from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash
from db.models import Userdb

User_db = Userdb()


def authenticate_user_for_attendance(user_uid, pwd):
    user_profile = User_db.get_user_by_uid(user_uid)
    
    
    if user_profile:
        authenticated = check_password_hash(user_profile["hashed_pwd"], pwd)
        if authenticated:
            return True
        else:
            return False
        
    else:
        return False

def decrypt(enc_text):
    scrambled_text = ""
    c = len(enc_text)
    clear_text = [''] * c
    last_index = c - 1

    half_length = c // 2 if c % 2 == 0 else (c // 2) + 1

    for i in range(c):
        a = ord(enc_text[i]) - 10
        a_char = chr(a)
        scrambled_text += a_char

    if c % 2 == 0:
        for i in range(half_length):
            clear_text[i] = scrambled_text[2 * i]
            clear_text[last_index - i] = scrambled_text[2 * i + 1]
    else:
        for i in range(half_length):
            clear_text[i] = scrambled_text[2 * i]
            if (half_length - i) > 1:
                clear_text[last_index - i] = scrambled_text[2 * i + 1]

    return ''.join(clear_text)


# print(decrypt("=;9D=<9;<D::C*C"))
