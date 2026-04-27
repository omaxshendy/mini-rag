# Studying project?

### command to insall all required packages
```
pip install -r requirements.txt
```

### command to run uvicorn

``` 
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```
### command to run docker in the background
Make sure to change directory to the docker folder
```
cd docker
```
#### runs docker:
```
sudo docker compose up -d
```

### commands to set env
```
conda env list
conda activate miniragENV
```