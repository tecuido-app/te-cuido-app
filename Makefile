.PHONY: install agent dashboard demo-fall demo-low-hr demo-low-spo2 reset clean

install:
	cd agent && pip install -r requirements.txt
	cd dashboard && npm install

agent:
	uvicorn agent.api:app --reload --port 8000

dashboard:
	cd dashboard && npm run build && npm start

# Comandos de demo — disparan el agente sin MQTT
demo-fall:
	curl -s -X POST "http://localhost:8000/api/simulate?event_type=fall" | python3 -m json.tool

demo-low-hr:
	curl -s -X POST "http://localhost:8000/api/simulate?event_type=low_hr" | python3 -m json.tool

demo-low-spo2:
	curl -s -X POST "http://localhost:8000/api/simulate?event_type=low_spo2" | python3 -m json.tool

reset:
	curl -s -X POST "http://localhost:8000/api/wellbeing" | python3 -m json.tool

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .next -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
