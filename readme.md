## To run FastAPI, use command:
```
gunicorn FastApiT1:app -k uvicorn.workers.UvicornWorker --workers 8 --bind 0.0.0.0:8000 --log-level critical
```

## To run Litestar, use command:
```
uvicorn LitestarT1:app --workers 8 --worker-class uvicorn.workers.UvicornWorker --log-level critical --keep-alive 5 --port 9000
```


## To run Gin, use command:
```
go build -o test
./test
```

