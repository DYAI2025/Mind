import json
import urllib.request
import urllib.parse
import pytest
import subprocess
import time
import sys
import os

def test_knowledge_sharing_api():
    """Test the knowledge sharing API endpoints"""
    # Start the API server in the background
    env = os.environ.copy()
    env['API_PORT'] = '8010'  # Use different port for testing
    
    proc = subprocess.Popen([sys.executable, 'mind_bus_api.py'], env=env)
    time.sleep(2)  # Wait for server to start
    
    try:
        base_url = "http://localhost:8010"
        
        # Test storing knowledge
        knowledge_data = {
            "title": "Test Knowledge Entry",
            "content": "This is a test knowledge entry for AI sharing",
            "category": "shared",
            "tags": ["test", "api"],
            "author": "test_agent"
        }
        
        # POST new knowledge
        data = json.dumps(knowledge_data).encode()
        req = urllib.request.Request(f"{base_url}/knowledge", data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req) as resp:
            assert resp.getcode() == 200
            result = json.loads(resp.read().decode())
            entry_id = result['id']
            assert result['title'] == knowledge_data['title']
            assert result['author'] == knowledge_data['author']
            assert 'created_at' in result
        
        # GET knowledge by ID
        req = urllib.request.Request(f"{base_url}/knowledge/{entry_id}")
        with urllib.request.urlopen(req) as resp:
            assert resp.getcode() == 200
            result = json.loads(resp.read().decode())
            assert result['id'] == entry_id
            assert result['title'] == knowledge_data['title']
        
        # Query knowledge
        req = urllib.request.Request(f"{base_url}/knowledge?category=shared")
        with urllib.request.urlopen(req) as resp:
            assert resp.getcode() == 200
            results = json.loads(resp.read().decode())
            assert len(results) >= 1
            assert any(r['id'] == entry_id for r in results)
        
        # Update knowledge
        updated_data = knowledge_data.copy()
        updated_data['content'] = "Updated content for testing"
        data = json.dumps(updated_data).encode()
        req = urllib.request.Request(f"{base_url}/knowledge/{entry_id}", data=data, method='PUT')
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req) as resp:
            assert resp.getcode() == 200
            result = json.loads(resp.read().decode())
            assert result['content'] == updated_data['content']
            assert 'updated_at' in result
        
        # Delete knowledge
        req = urllib.request.Request(f"{base_url}/knowledge/{entry_id}", method='DELETE')
        with urllib.request.urlopen(req) as resp:
            assert resp.getcode() == 200
        
        # Verify deletion
        try:
            req = urllib.request.Request(f"{base_url}/knowledge/{entry_id}")
            urllib.request.urlopen(req)
            assert False, "Should have returned 404"
        except urllib.error.HTTPError as e:
            assert e.code == 404
        
        print("✅ All knowledge sharing API tests passed!")
        
    finally:
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    test_knowledge_sharing_api()