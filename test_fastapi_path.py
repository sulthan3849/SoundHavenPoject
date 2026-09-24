from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/test/{item_id}")
def test_route(item_id: str):
    return {"item_id": item_id}

client = TestClient(app)
print(client.get("/test/..%2f..%2ffoo").json())
