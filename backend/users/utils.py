import secrets

# function to generate OTP for verify emails.
def generate_secure_verification_code(length=6):
    digits = "0123456789"
    otp = ''.join(secrets.choice(digits) for _ in range(length))

    return otp