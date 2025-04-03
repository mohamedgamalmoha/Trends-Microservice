test-install-requirements:
	pip install -r requirements-dev.txt

test-pre-run: test-install-requirements 

test-post-run: 

test-run:
	pytest -v -p no:warnings --asyncio-mode=auto --tb=short

test: test-pre-run test-run test-post-run
