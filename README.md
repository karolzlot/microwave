## How to run

Start redis:

```
docker run --name redis-microwave1 -p 6379:6379 -d redis
```

Create a virtual environment and install dependencies (poetry is required):

```
poetry install
```

Run the application:

```
python -m main
```
