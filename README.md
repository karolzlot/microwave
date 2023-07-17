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


## TODO:

- [ ] Add more and better tests
- [ ] Improve code organization / refactor
- [ ] Add more documentation
- [ ] Add CI/CD
- [ ] Show error messages in frontend if backend sends errors or if the connection is lost
