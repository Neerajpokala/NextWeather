import requests
import pandas as pd

def get_nws_alerts_csv(state, filename):
    """
    Downloads all active NWS alerts for the specified US state (use two-letter code, e.g., 'TX', 'NY')
    and saves the full parsed data as a CSV.
    """
    url = f"https://api.weather.gov/alerts/active?area={state.upper()}"
    resp = requests.get(url, headers={"User-Agent": "weather-app"})
    data = resp.json()
    alerts = []
    for alert in data.get("features", []):
        prop = alert.get("properties", {})
        alerts.append(prop)          
    df = pd.DataFrame(alerts)
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} alerts to {filename}")


get_nws_alerts_csv("TX", "tx_alerts.csv")


