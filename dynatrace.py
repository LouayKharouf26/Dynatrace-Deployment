import requests
import csv
import matplotlib.pyplot as plt
from datetime import datetime

# Dynatrace API configuration
DT_API_TOKEN = ""
DT_BASE_URL = "https://stm14109.live.dynatrace.com/api/v2/metrics/query"

# Query parameters for carbon measurement
carbon_query = """
fetch bizevents
| filter contains (event.provider, "dynatrace.biz.carbon")
| filter contains (event.type, "carbon.measurement")
| summarize totalEnergy = sum(energy.measurement.computing), totalCO2e = sum(carbon.emissions), by:dt.entity.host
"""
carbon_url = "https://stm14109.live.dynatrace.com/api/v2/events"  


headers = {
    "Authorization": f"Api-Token {DT_API_TOKEN}"
}


response_carbon = requests.get(carbon_url, headers=headers, params={"query": carbon_query})

if response_carbon.status_code == 200:
    carbon_data = response_carbon.json()


    host_names = []
    total_energy = []
    total_co2e = []

    if "result" in carbon_data:
        for event in carbon_data["result"]:
            host_names.append(event.get("dt.entity.host", "Unknown"))
            total_energy.append(event.get("totalEnergy", 0))
            total_co2e.append(event.get("totalCO2e", 0))
    else:
        print("No carbon measurement data found.")

   
    metric_selector = "builtin:host.cpu.usage" 
    timeframe = "now-1h"  
    params = {
        "metricSelector": metric_selector,
        "resolution": "1m"  
    }

    # Fetch CPU usage data
    response_cpu = requests.get(DT_BASE_URL, headers=headers, params=params)

    # Check if the request was successful for CPU data
    if response_cpu.status_code == 200:
        data = response_cpu.json()

        # Parse and save to CSV
        timestamps_list = []
        values_list = []
        if "result" in data and data["result"]:
            metric_results = data["result"][0]
            with open("metrics.csv", "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                # Write header with Host, CPU Usage, Energy, CO2
                writer.writerow(["Timestamp", "Value", "Host", "Total Energy", "Total CO2e"])

                # Extract and write metric data
                if "data" in metric_results:
                    for datapoint in metric_results["data"]:
                        timestamps = datapoint.get("timestamps", [])
                        values = datapoint.get("values", [])
                        for ts, value in zip(timestamps, values):
                           
                            host = host_names.pop(0) if host_names else "Unknown"
                            energy = total_energy.pop(0) if total_energy else 0
                            co2e = total_co2e.pop(0) if total_co2e else 0
                            
                            # Write data to CSV
                            writer.writerow([ts, value, host, energy, co2e])
                            timestamps_list.append(datetime.utcfromtimestamp(ts / 1000))  # Convert from ms to datetime
                            values_list.append(value)

            print("Metrics with carbon data saved to metrics.csv")

            plt.figure(figsize=(10, 5))
            plt.plot(timestamps_list, values_list, marker='o', linestyle='-', color='b')
            plt.title("CPU Usage Over Time")
            plt.xlabel("Time")
            plt.ylabel("CPU Usage (%)")
            plt.grid()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig("plot.png")
            plt.show()
        else:
            print("No CPU data found or invalid response format.")
    else:
        print(f"API call for CPU data failed with status code {response_cpu.status_code}: {response_cpu.text}")
else:
    print(f"API call for carbon data failed with status code {response_carbon.status_code}: {response_carbon.text}")
