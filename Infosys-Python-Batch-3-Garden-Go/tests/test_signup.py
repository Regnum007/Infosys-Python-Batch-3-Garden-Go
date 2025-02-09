def test_signup(client):
    # Test GET request to `/signup`
    response = client.get('/signup')
    # Ensure the signup page loads

    # Test POST request to `/signup`
    response = client.post('/signup', data={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'mobile': '1234567890',
        'password': 'password123',
        'role': 'Customer',  # Ensure this matches your form's `role` field
    })
   
