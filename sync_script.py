name: Automated Renpho Garmin Sync

on:
  schedule:
    - cron: '0 */6 * * *' # Wakes up automatically every 6 hours
  workflow_dispatch:     # Keeps your manual sync button active

jobs:
  sync-metrics:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Sync Dependencies
        run: |
          pip install requests
          pip install garminconnect

      - name: Download and Run Sync Script
        run: |
          wget https://githubusercontent.com
          python renpho_to_garmin.py --renpho-email "${{ secrets.RENPHO_EMAIL }}" --renpho-password "${{ secrets.RENPHO_PASSWORD }}" --garmin-email "${{ secrets.GARMIN_EMAIL }}" --garmin-password "${{ secrets.GARMIN_PASSWORD }}"

