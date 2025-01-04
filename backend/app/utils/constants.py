from app.utils.fetch_data import get_required_env_var

# Secret keys for JWT tokens
JWT_SECRET = get_required_env_var("JWT_SECRET_KEY")
JWT_REFRESH_SECRET = get_required_env_var("JWT_REFRESH_SECRET_KEY")
JWT_HASHING_ALGO = get_required_env_var("JWT_HASHING_ALGO")

# Define token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


MACHINE_ID = int(get_required_env_var("MACHINE_ID"))
