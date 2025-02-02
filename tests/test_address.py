import pytest
from flask import json
from main import create_app, db

import pytest
from flask import json
import pytest
from flask import json

def test_set_default_address(client):
    """Test setting a default address"""
    new_address = {
        "user_id": 1,
        "address": "123 Main St, City, Country",
        "is_default": True
    }
    response = client.post("/address", data=json.dumps(new_address), content_type="application/json")
   

def test_update_address(client):
    """Test updating an existing address"""
    update_data = {
        "address": "456 New St, City, Country"
    }
    response = client.put("/address/1", data=json.dumps(update_data), content_type="application/json")
    

def test_delete_address(client):
    """Test deleting an address"""
    response = client.delete("/address/1")
   
