# Aeon Bot

Bot for Discord.

## Requirements
- Python >3.10
- [Aeon API](https://github.com/renaism/aeon-api)

## Usage
- Clone the repository
```bash
git clone https://github.com/renaism/aeon-bot.git &&\
cd aeon-bot
```

- Create and activate python virtual environment
```bash
python -m venv venv &&\
source venv/bin/activate
```

- Install requirements
```bash
pip install --no-deps -r requirements.txt
```

- Configure environment variables
```bash
touch .env
```

```
# .env

ENV=development

# Insert your Discord Bot token here
TOKEN=XXX

# Insert the API URL here
API_URL=http://127.0.0.1:8000

# Insert the API key here
API_KEY=XXX
```

- Start the bot
```bash
python main.py
```