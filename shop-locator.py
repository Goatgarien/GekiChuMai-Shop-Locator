import time
import requests
from bs4 import BeautifulSoup  # For parsing HTML content
import csv
from url_extensions import prefectures, games  # Importing the prefectures and games data
    
def get_store_data(store_data, prefecture_name, prefecture, game):
    headers = {
            # Include cookies from browser's "Request Headers" (if necessary)
            # "Cookie": "facility_dspcount=50",  # Replace with actual cookie values
        }
    base_url = f"https://location.am-all.net/alm/location?lang=en{game['value']}{prefecture.get('url_extension', '')}"
    response = requests.get(base_url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    store_elements = soup.select('ul.store_list > li')

    for store_element in store_elements:
        location_name = store_element.find('span', class_='store_name').text.strip()
        address = store_element.find('span', class_='store_address').text.strip()

        map_button = store_element.find('button', class_='store_bt_google_map_en')
        map_link = map_button['onclick']
        map_url_part = map_link.split("window.open('")[1].split("')")[0]
        maps_url = f"https:{map_url_part}"
        lat_lon_part = map_url_part.rsplit('@', 1)[-1].split('&')[0]
        lat_lon = lat_lon_part.split(',')

        latitude = lat_lon[0]
        longitude = lat_lon[1]

        if location_name in store_data:
            # Update game availability for existing location
            store_data[location_name][game['key']] = True # Set current game key as supported for the existing location
        else:
            # Create new store info for a new location
            store_info = {
                "name": location_name,
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
                "maps_url": maps_url,
                "region": prefecture['region'],
                "prefecture": prefecture_name,
                "MaiDX": False,
                "MaiDXInt": False,
                "Chuni": False,
                "ChuniInt": False,
                "Ongeki": False,
                "Diva": False,
            }
            # Set current game as supported for the new location
            store_info[game['key']] = True

            # Add new store info to store_data dictionary
            store_data[location_name] = store_info

    return store_data



def save_to_csv(data, filename, encoding='utf-8-sig'):
    with open(filename, 'w', newline='', encoding=encoding) as csvfile:
        # Get fieldnames from the first data point in the dictionary
        fieldnames = next(iter(data.values())).keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for store in data.values():
            writer.writerow(store)


def main():
    all_store_data = {}
    #for loops to iterate through prefectures and games found in url-extensions.py
    for prefecture_name, prefecture in prefectures.items():
        for game_name, game_value in games.items():
            game = {'key': game_name, 'value': game_value}
            print(f"Getting store data for {game_name} in {prefecture_name}")
            all_store_data = get_store_data(all_store_data, prefecture_name, prefecture, game)
            time.sleep(0.15)

    save_to_csv(all_store_data, "store_data.csv")
    print("Store data saved to store_data.csv")

if __name__ == "__main__":
    main()
