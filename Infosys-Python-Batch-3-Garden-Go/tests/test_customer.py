

def test_customer_page_logged_in(client):
    # Register a new user
    client.post('/signup', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'mobile': '1234567890',
        'password': 'password',
        'role': 'Customer'
    })
    
    # Login the user
    client.post('/login', data={'email': 'test@example.com', 'password': 'password'})
    
  

def test_customer_page_not_logged_in(client):
    # Test accessing the customer page without being logged in
    response = client.get('/customer')
  
