def test_view_addresses(client):
    # Register and login the user
    client.post('/signup', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'mobile': '1234567890',
        'password': 'password',
        'role': 'Customer'
    })
    client.post('/login', data={'email': 'test@example.com', 'password': 'password'})
    
    # Add some addresses manually or via another route
    client.post('/add-address', data={
        'street_address': '123 Main St',
        'locality': 'Locality 1',
        'city': 'City 1',
        'state': 'State 1',
        'postal_code': '12345'
    })
    client.post('/add-address', data={
        'street_address': '456 Another St',
        'locality': 'Locality 2',
        'city': 'City 2',
        'state': 'State 2',
        'postal_code': '67890'
    })
    
  
