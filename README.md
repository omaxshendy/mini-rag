# Studying project?

### command to insall all required packages
```
pip install -r requirements.txt
```

## Running code
### you run from `src` directory
```
cd src
```

### commands to set env
```
conda env list
conda activate miniragENV
```
### command to run uvicorn
``` 
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

Error: ERROR:    Error loading ASGI app. Could not import module "main".
- Happens when you don't cd src (as `main` is inside the `src` directory) and if you're not in that directory it wont be able to read it

### command to run docker in the background
Make sure to change directory to the docker folder
```
cd docker
```
#### runs docker:
```
sudo docker compose up -d
```

