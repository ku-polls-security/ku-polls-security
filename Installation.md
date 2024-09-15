# Installation steps

## 1. Clone repository

- Clone this repository to your local computer.

```
git clone https://github.com/TAGCH/ku-polls.git DirectoryName
```
**NOTED**: ```DirectoryName``` is your desired directory name.

## 2. Create virtual environment and install dependencies

- Create virtual environment.

```
python -m venv env
```

- Change to your newly created virtual environment.

For Mac and Linux.
```
source env/bin/activate
```
For Window.
```
env\Scripts\activate.bat
```

- Install packages from requirements.txt

```
pip install -r requirements.txt
```

## 3. Set values for externalized variables
- Create file `.env` to configuration and get the secret key [Secret Key](https://djecrety.ir)

- Copy code from [sample.env](sample.env) and paste it in `.env`

- Set `DEBUG=True`

## 4. Run migration

- Run migration.

```
python manage.py migrate
```

## 5. Run tests

- Checking all tests.

```
python manage.py test
```

## 6. Install data from the data fixtures

- Load data.

```
python manage.py loaddata data/polls-v4.json data/votes-v4.json data/users.json
```