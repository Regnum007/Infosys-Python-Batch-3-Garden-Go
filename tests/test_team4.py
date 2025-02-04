import pytest

# ===========================
# General API & Authentication Tests
# ===========================

def test_api_sales_data(client):
    response = client.get('/api/sales-data')
   

def test_api_generate_graph_missing_fields(client):
    incomplete_payload = {
        "analysisType": "daily"  # Missing dates
    }
    response = client.post('/api/generate-graph', json=incomplete_payload)
    
def test_protected_route_without_login(client):
    response = client.get('/sales_graph')
   

def test_protected_route_with_login(client):
    with client.session_transaction() as session:
        session['logged_in'] = True
    response = client.get('/sales_graph')
    
def test_logout(client):
    with client.session_transaction() as session:
        session['logged_in'] = True
    response = client.get('/logout')
   
def test_index_page(client):
    response = client.get('/')
    
def test_sales_graph_page(client):
    response = client.get('/sales_graph')
  

# ===========================
# Delivery Dashboard Tests
# ===========================

def test_delivery_dashboard_page(client):
    response = client.get('/delivery_dashboard')
    

def test_delivery_data_api(client):
    response = client.get('/api/delivery-data')
   

    data = response.get_json()
    
   

def test_sales_data_api(client):
    response = client.get('/api/sales-data')
   
    data = response.get_json()
   
    

# ===========================
# Heatmap Tests (Now using Product_popularity_graph.html)
# ===========================

def test_initial_render(client):
    response = client.get('/product_popularity_graph')  # Corrected route
    print("\n==== Response Data (Initial Render) ====\n", response.data.decode())  # Debugging output
    

def test_search_functionality(client):
    response = client.get('/product_popularity_graph')  # Corrected route
    print("\n==== Response Data (Search Functionality) ====\n", response.data.decode())  # Debugging output
    
def test_heatmap_generation(client):
    response = client.get('/product_popularity_graph')  # Corrected route
    print("\n==== Response Data (Heatmap Generation) ====\n", response.data.decode())  # Debugging output
    

def test_region_info_click(client):
    response = client.get('/product_popularity_graph')  # Updated route
    print(response.data.decode())  # Debugging output
    

# ===========================
# Invalid Route Tests
# ===========================

def test_invalid_endpoint(client):
    response = client.get('/invalid-endpoint')
    
def test_invalid_route(client):
    response = client.get('/invalid-route')
   