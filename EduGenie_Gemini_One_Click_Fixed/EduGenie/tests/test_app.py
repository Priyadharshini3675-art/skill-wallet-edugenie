import os
os.environ["DEMO_MODE"] = "true"  # Health display only; features use mocked provider
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home_and_health():
    page = client.get("/")
    assert page.status_code == 200
    assert "EduGenie" in page.text
    assert client.get("/static/app.js").status_code == 200
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["mode"] == "demo"

def test_five_features(monkeypatch):
    import json
    import qna, explanation_module, summary_module, quiz_module, learning_path
    def fake_generate(prompt, *, json_output=False, max_tokens=2048):
        if json_output:
            return json.dumps({'questions': [
                {'question': f'What is the answer for sample {i}?',
                 'options': ['A', 'B', 'C', 'D'], 'answer': 'A',
                 'explanation': 'Mock educational explanation'} for i in range(3)]})
        return 'A realistic AI response mocked for automated tests.'
    for module in (qna, explanation_module, summary_module, quiz_module, learning_path):
        monkeypatch.setattr(module, 'generate', fake_generate)

    a=client.get("/qa",params={"question":"What is the Pacific Ocean?"})
    assert a.status_code==200 and a.json()["answer"]
    b=client.post("/explain",json={"topic":"Photosynthesis","level":"beginner"})
    assert b.status_code==200 and b.json()["explanation"]
    c=client.post("/summarize",json={"text":"Photosynthesis converts sunlight into chemical energy."})
    assert c.status_code==200 and c.json()["summary"]
    d=client.post("/quiz",json={"text":"Pythagorean theorem"})
    assert d.status_code==200 and len(d.json()["quiz"])==3
    assert all(q["answer"] in q["options"] for q in d.json()["quiz"])
    e=client.post("/learn/recommendations",json={"topic":"SQL","level":"beginner","weeks":4})
    assert e.status_code==200 and e.json()["recommendation"]
    f=client.get("/learn/recommendations",params={"topic":"SQL"})
    assert f.status_code==200

def test_validation():
    assert client.post("/summarize",json={"text":""}).status_code==422
    assert client.post("/explain",json={"topic":"math","level":"expert"}).status_code==422
    assert client.post("/learn/recommendations",json={"topic":"SQL","weeks":100}).status_code==422

def test_api_key_error(monkeypatch):
    from ai_client import _client
    monkeypatch.setenv("DEMO_MODE","false")
    monkeypatch.delenv("GEMINI_API_KEY",raising=False)
    _client.cache_clear()
    resp=client.get("/qa",params={"question":"What is water?"})
    assert resp.status_code==503
    assert "key" in resp.json()["detail"].lower()
