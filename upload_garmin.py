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

    # 👇 FIXED: We move the imports INSIDE the function. 
    # This physically blocks the library from running an auto-login test on script boot!
    print("Loading Garmin connect libraries safely inside isolation pipeline...")
    from garminconnect import Garmin
    import garth

    print("Connecting to Garmin Connect via secondary isolated script...")
    token_dir = os.path.join(os.getcwd(), ".garminconnect")
    
    # Check if your file is actually where it's supposed to be
    nested_token_file = os.path.join(token_dir, "garmin.tokens.json")
    if not os.path.exists(nested_token_file):
        print(f"Error: Token file missing at '{nested_token_file}'! Re-check your GitHub folder paths.")
        sys.exit(1)

    try:
        # Initialize cleanly without any extra unneeded keywords
        garmin = Garmin(
            email=args.garmin_email, 
            password=args.garmin_password
        )
        
        # 👇 Tell the library that the login status is already pre-verified by your token file
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
