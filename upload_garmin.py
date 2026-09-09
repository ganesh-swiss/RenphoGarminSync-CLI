import sys
import argparse
import os
import warnings

# Completely suppress upstream deprecation noise
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

    print("Loading Garmin connect libraries safely inside isolation pipeline...")
    from garminconnect import Garmin

    print("Connecting to Garmin Connect via secondary isolated script...")
    token_dir = os.path.join(os.getcwd(), ".garminconnect")
    
    if not os.path.exists(token_dir) or not os.listdir(token_dir):
        print(f"Error: Token directory '{token_dir}' is missing or empty! Ensure you uploaded your token files to GitHub.")
        sys.exit(1)

    try:
        # 👇 FIXED: Instantiated without a password parameter!
        # This completely strips out the background online login scripts,
        # forcing the library to run entirely offline against your saved token file.
        print(f"Initializing offline native engine for: {args.garmin_email}")
        garmin = Garmin(email=args.garmin_email)
        
        # Pull your pre-authorized token profile file directly from the workspace repository 
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
