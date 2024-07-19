def test_base_endpoint(client):
    """
    Test case for the base endpoint ("/").
    This test verifies that the base endpoint is reachable and responds with a 200 OK status.
    It also checks that the response JSON contains a status key with the value "ready",
    indicating that the server is up and running.
    """
    response = client.get("/")
    assert response.status_code == 200  # Verify that the response status code is 200 OK
    
    status = response.json["status"]
    assert status == "ready"  # Verify that the response JSON contains status "ready"

def test_invalid_endpoint(client, h_principal):
    """
    Test case for an invalid endpoint ("/something").
    This test ensures that the server returns a 404 Not Found status when accessing
    an endpoint that does not exist. It verifies that the server properly handles
    requests to non-existent endpoints.
    """
    response = client.get("/something", headers=h_principal)
    assert response.status_code == 404  # Verify that the response status code is 404 Not Found
