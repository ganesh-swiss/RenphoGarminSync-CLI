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
    
    # Structural check to make sure the token folder path exists
    os.makedirs(token_dir, exist_ok=True)

    try:
        from garminconnect import Garmin
        import garth
        
        # 👇 FIXED: Pass password=None and verify_login=False right into initialization!
        # This completely strips out the automatic startup login script, 
        # dropping the 429/403 Cloudflare blocks instantly!
        garmin = Garmin(
            email=args.garmin_email, 
            password=None,
            verify_login=False
        )
        
        # 👇 FIXED: Instruct Garth's underlying core to pull the locally saved files directly 
        # without running cross-machine confirmation handshakes.
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
