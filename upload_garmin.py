import sys
import argparse
import os
import warnings

# Silence the Garth retirement text warnings completely
warnings.filterwarnings("ignore", category=DeprecationWarning)

from datetime import datetime

def upload():
    parser = argparse.ArgumentParser()
    parser.add_argument('--garmin-email', required=True)
    parser.add_argument('--garmin-password', required=True)
    parser.add_argument('--weight', required=True, type=float)
    parser.add_argument('--fat', required=True, type=float)
    parser.add_argument('--bmi', required=True, type=float)
    args = parser.parse_args()

    print("Connecting to Garmin Connect via secondary isolated script...")
    token_dir = os.path.join(os.getcwd(), ".garminconnect")
    os.makedirs(token_dir, exist_ok=True)

    try:
        from garminconnect import Garmin
        import garth
        
        # Initialize with password=None to completely kill the background web logins
        # This safely stops the script from triggering Cloudflare 429/403 blocks!
        garmin = Garmin(
            email=args.garmin_email, 
            password=None
        )
        
        # 👇 FIXED: Tell the library that the login status is pre-verified.
        # This explicitly stops Garth from verifying the token's cross-machine origin.
        garmin.is_login_verified = True
        
        # Load your local token file directly from the repository directory
        print(f"Loading environment-specific cloud tokens from: {token_dir}")
        garmin.login(token_dir)
        
        # Execute health metric injection
        today_str = datetime.now().strftime("%Y-%m-%d")
        garmin.add_body_composition(
            timestamp=today_str,
            weight=args.weight,
            percent_fat=args.fat,
            bmi=args.bmi
        )
        print("Success: Stats injected successfully into Garmin Connect!")
        
    except Exception as e:
        print(f"Error: Garmin Connection Failed. Reason: {e}")
        sys.exit(1)

if __name__ == "__main__":
    upload()
