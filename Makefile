.PHONY: start install install-dev test demo-fall demo-low-hr demo-low-spo2 reset bump-patch bump-minor bump-major clean

# One-command deploy (Docker)
start:
	./start.sh

# Install runtime dependencies locally (without Docker)
install:
	cd agent && pip install -r requirements.txt
	cd dashboard && npm install

# Install dev dependencies (testing + versioning tools)
install-dev:
	pip install -r requirements-dev.txt

# Run test suite
test:
	python -m pytest -v

# Demo shortcuts (requires agent running on :8000)
demo-fall:
	./demo.sh fall

demo-low-hr:
	./demo.sh low_hr

demo-low-spo2:
	./demo.sh low_spo2

reset:
	./demo.sh reset

# Version bumping — commits + tags automatically
bump-patch:
	bump-my-version bump patch

bump-minor:
	bump-my-version bump minor

bump-major:
	bump-my-version bump major

# Remove build artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .next -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
