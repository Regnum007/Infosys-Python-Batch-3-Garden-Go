def test_index(client):
    response = client.get('/')
    