build:
	docker build -t api .

run:
	docker rm -f api-container || true
	docker run -d -p 8000:8000 --name api-container api

stop:
	docker stop api-container || true && docker rm api-container || true