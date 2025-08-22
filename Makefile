build:
	docker build -t api .

run:
	docker rm -f api-container || true
	docker run -d -p 80:80 --name api-container api

stop:
	docker stop api-container || true && docker rm api-container || true