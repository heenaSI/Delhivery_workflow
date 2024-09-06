# Import necessary modules from Flask framework and other libraries
import xmlrpc.client
import json
import yaml
import os

import sys

def main():

    date = sys.argv[1]  # if len(sys.argv) > 1 else "2024-09-04"
    # Use the date variable in your script logic
    print(f"Extracting orders for date: {date}")

    # Function to save order details to a file
    def save_order_to_file(order_name, order_data, file_format='json'):
        # Create a directory for saving files if it doesn't exist
        if not os.path.exists('orders'):
            os.makedirs('orders')

        # Determine file extension and file path
        file_extension = 'json' if file_format == 'json' else 'yaml'
        file_path = os.path.join('orders', f'{order_name}.{file_extension}')
        
        # Save data to JSON or YAML file
        if file_format == 'json':
            with open(file_path, 'w') as json_file:
                json.dump(order_data, json_file, indent=4)
        elif file_format == 'yaml':
            with open(file_path, 'w') as yaml_file:
                yaml.dump(order_data, yaml_file, default_flow_style=False)


    # Set up credentials and URL for Odoo instance
    url = 'https://sweet-indulgence.odoo.com/'
    db = 'sweet-indulgence'
    username = 'heena.sweetindulgence@gmail.com'
    password = 'ZxcRtyBnm@101'

    # Authenticate and get session ID from Odoo
    session_url = f'{url}web/session/authenticate'
    data = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            "service": "common",
            "method": "login",
            'db': db,
            'login': username,
            'password': password,
        }
    }

    # Authenticate
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})

    # Create a connection to Odoo
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    order_ids = models.execute_kw(
        db, uid, password, 'sale.order', 'search',
        [[['state', '=', 'sale'], ['date_order', '>=', date+' 00:00:00'], ['date_order', '<=', date+' 23:59:59']]],  # Filters for confirmed eCommerce orders only
        {'limit': 10, 'order': 'create_date desc'}
    )

    print(order_ids)

    order_details = models.execute_kw(
            db, uid, password, 'sale.order', 'read', [order_ids], 
            {'fields': ['name', 'partner_id', 'date_order', 'amount_total', 'order_line']}
        )

    for order in order_details:

        amzn = False

        # print(order.keys())

        order_line_ids = order['order_line']
        # order_line_details = models.execute_kw(
        #             db, uid, password, 'sale.order.line', 'read', [order_line_ids],
        #             {'fields': ['product_id', 'name', 'product_uom_qty', 'price_unit']})
        
        order_line_details = models.execute_kw(
                    db, uid, password, 'sale.order.line', 'read', [order_line_ids])

        if order_line_details[0]['name_short']=='Amazon Sale':
            amzn=True
        
        partner_id = order['partner_id'][0]
        partner_details = models.execute_kw(
                db, uid, password, 'res.partner', 'read', [partner_id],
                # {'fields': ['name', 'street', 'city', 'zip', 'state_id', 'country_id']}
            )
        
        # print(partner_details[0].keys())
        # print(partner_details[0]['phone'])
        # print(partner_details[0]['mobile'])
        # name = partner_details[0]['name']
        # street_address = partner_details[0]['street']
        # city = partner_details[0]['city']
        # zip = partner_details[0]['zip']
        # country = partner_details[0]['country_id'][1]
        # state = partner_details[0]['state_id'][1]

        order_data = {
            'customer': {
                'name': partner_details[0]['name'],
                'street_address': partner_details[0]['street'],
                'city': partner_details[0]['city'],
                'state': partner_details[0]['state_id'][1][:-5],
                'zip': partner_details[0]['zip'],
                'country': partner_details[0]['country_id'][1],
                'phone':partner_details[0]['phone']
            },
            'date_order': order['date_order'],
            'Total_amount': order['amount_total'],
            'order_id': order['name'], 
            'products': []
        }

        for line in order_line_details:
            product_id = line['product_id'][0]
            if 'Shipping' in line['product_template_id'][1]:
                continue
            # Fetch the product details, including the category
            product_details = models.execute_kw(
                db, uid, password, 'product.product', 'read', [product_id],
                {'fields': ['categ_id']})
            
            # Extract the category information
            product_category = product_details[0]['categ_id'][1]  # This will give the category name

            product_data = {
                'product_name': line['name'],
                'product_category': product_category,
                'product_name_short': line.get('name_short', 'N/A'),  # Safeguard for missing 'name_short'
                'quantity': line['product_uom_qty'],
                'price': line['price_unit']
            }
            order_data['products'].append(product_data)

        order_name = order['id']  # Assuming 'name' is the order's unique identifier
        save_order_to_file(order_name, order_data, file_format='json')

if __name__ == "__main__":
    main()