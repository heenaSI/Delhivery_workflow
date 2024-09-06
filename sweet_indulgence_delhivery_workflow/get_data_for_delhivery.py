import json
import requests
import os
import sys

def create_delhivery_order(file, pickup_date):
    with open(file) as json_file:
        data = json.load(json_file)

    order = data['order_id']
    name = data['customer']['name']
    # name = urllib.parse.quote(name)
    address = data['customer']['street_address']
    pincode = data['customer']['zip']
    city = data['customer']['city']
    state = data['customer']['state']
    phone_no = data['customer']['phone']
    total_amount = data["Total_amount"]

    quantity = 0
    cookies_count = 0
    bars_count = 0
    granola_count = 0
    butter_count = 0
    total_quantity = 0

    for p in data['products']:
        total_quantity +=p["quantity"]
        if 'Cookies' in p['product_category']:
            cookies_count+=p["quantity"]
        elif 'Bars' in p['product_category']:
            bars_count+=quantity
        elif 'Granola' in p['product_category']:
            granola_count+=p["quantity"]
        elif 'Butter' in p['product_category']:
            butter_count+=p["quantity"]

    number_of_cookie_box = cookies_count + granola_count/2 + bars_count/2
    weight = cookies_count*220+ granola_count*170 + bars_count*200 + butter_count*200


    if number_of_cookie_box==1:
        shipment_width="14.0"
        shipment_height="11.5"
        shipment_length="16.0"
    elif number_of_cookie_box==2:
        shipment_width="22.5"
        shipment_height="14.0"
        shipment_length="16.0"
    elif number_of_cookie_box==3 or number_of_cookie_box==4:
        shipment_width="27.5"
        shipment_height="22.5"
        shipment_length="16.0"
    elif number_of_cookie_box==5 or number_of_cookie_box==6:
        shipment_width="33.5"
        shipment_height="27.5"
        shipment_length="16.0"
    elif number_of_cookie_box==7 or number_of_cookie_box==8:
        shipment_width="27.5"
        shipment_height="22.5"
        shipment_length="30.0"
    else:
        shipment_width="14.0"
        shipment_height="11.5"
        shipment_length="16.0"

    # URL
    url = "https://track.delhivery.com/api/cmu/create.json"

    # Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Token 375c7a951579131d9885a149fa111fef71a6b2f0"
    }

    # Data payload
    data = {
        "shipments": [
            {
                "name": name,
                "add": address,
                "pin": pincode,
                "city": city,
                "state": state,
                "country": "India",
                "phone": phone_no,
                "order": order,
                "payment_mode": "Prepaid",
                "return_pin": "400082",
                "return_city": "Mumbai",
                "return_phone": "9699830446",
                "return_add": "0, 62-1-A, Mulund Colony, Guru Gobind Singh Marg, Mulund (W)",
                "return_state": "Maharashtra",
                "return_country": "India",
                "products_desc": "Cookies and Bars",
                "hsn_code": "19059020",
                "cod_amount": "0",
                "order_date": None,
                "total_amount": total_amount,
                "seller_add": "",
                "seller_name": "Sweet Indulgence",
                "seller_inv": "",
                "quantity": quantity,
                "waybill": "",
                "shipment_width": shipment_width,
                "shipment_height": shipment_height,
                "weight": weight,
                "seller_gst_tin": "27ACJPS3405J1ZE",
                "shipping_mode": "Surface",
                "address_type": "home"
            }
        ],
        "pickup_location": {
            "name": "Sweet Indulgence",
            "add": "0, 62-1-A, Mulund Colony, Guru Gobind Singh Marg, Mulund(W)",
            "city": "Mumbai",
            "pin_code": "400082",
            "country": "India",
            "phone": "9699830446"
        }
    }

    # Parameters
    params = {
        "format": "json",
        "data": json.dumps(data)
    }

    print("Creating Shipment ....")

    # Make the POST request
    response = requests.post(url, headers=headers, data=params)

    # Check if the request was successful
    if response.status_code == 200:
        waybill = response.json()['packages'][0]['waybill']
        print("Waybill: ", waybill)
    else:
        print("Failed to create shipment. Status code:", response.status_code)
        print("Response:", response.text)

    ########## UPDATE BOX SIZE ##########

    print("Updating box size ....")

    # Define the URL and headers
    url = "https://track.delhivery.com/api/p/edit"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Token 375c7a951579131d9885a149fa111fef71a6b2f0"
    }

    # Define the data payload
    data = {
        "waybill": waybill,
        "phone": phone_no,
        "name": name,
        "add": "",
        "product_details": "",
        "shipment_length": float(shipment_length),
        "shipment_width": float(shipment_width),
        "shipment_height": float(shipment_height),
        "weight": weight
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check if the request was successful
    if response.status_code == 200:
        print("Response:", response.json())
    else:
        print("Failed to update shipment. Status code:", response.status_code)
        print("Response:", response.text)

    ########## Print Shipping label ##########

    print("Printing shipping label ....")

    # Make the GET request
    response = requests.get(
        "https://track.delhivery.com/api/p/packing_slip?wbns="+str(waybill)+"&pdf=true",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Token 375c7a951579131d9885a149fa111fef71a6b2f0"
        }
    )

    data = response.json()
    html_link = data['packages'][0]['pdf_download_link']

    response = requests.get(html_link)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the content to a file
        with open("shipping_label_"+str(order)+".pdf", "wb") as file:
            file.write(response.content)
        print("PDF file downloaded successfully!")
    else:
        print("Failed to download the file. Status code:", response.status_code)

    ######### PICKUP ##########

    print("Creating Pickup ....")

    # Define the URL and headers
    url = "https://track.delhivery.com/fm/request/new/"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Token 375c7a951579131d9885a149fa111fef71a6b2f0"
    }

    # Define the data payload
    data = {
        "pickup_location": "Sweet Indulgence",
        "expected_package_count": "1",
        "pickup_date": pickup_date,
        "pickup_time": "10:00:00"
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Check if the request was successful
    if response.status_code == 201:
        print("Response:", response.json())
    else:
        print("Failed to create request. Status code:", response.status_code)
        print("Response:", response.text)

def find_json_files(directory):
  """
  Finds all JSON files in a directory and its subdirectories.

  Args:
    directory: The directory to search.

  Returns:
    A list of paths to all JSON files found.
  """
  json_files = []
  for root, _, files in os.walk(directory):
    for filename in files:
      if filename.endswith(".json"):
        json_files.append(os.path.join(root, filename))
  return json_files

# create_delhivery_order(file="./orders/36.json", pickup_date="2024-09-03")

files = find_json_files("./orders")

# pickup_date="2024-09-05"

pickup_date = sys.argv[1] # if len(sys.argv) > 1 else "2024-09-05"
# Use the pickup_date variable in your script logic
print(f"Creating shipping labels for date: {pickup_date}")

for file in files:
    create_delhivery_order(file, pickup_date)