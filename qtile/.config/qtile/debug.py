import urllib.request
import xml.etree.ElementTree as ET

url = "https://dd.weather.gc.ca/citypage_weather/xml/AB/s0000045_e.xml"

print(f"Fetching: {url}")

try:
    # Add a Fake User-Agent so we look like a browser
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=10) as response:
        print(f"Status: {response.status}")
        data = response.read()
        print("Data received. Parsing...")

        root = ET.fromstring(data)

        # Debug: Check if tags exist
        temp = root.find(".//currentConditions/temperature")
        cond = root.find(".//currentConditions/condition")

        if temp is not None:
            print(f"Temperature Found: {temp.text}")
        else:
            print("ERROR: <temperature> tag is MISSING in the XML.")

        if cond is not None:
            print(f"Condition Found: {cond.text}")
        else:
            print("WARNING: <condition> tag is MISSING.")

except Exception as e:
    print("\nCRASH REPORT:")
    print(e)
