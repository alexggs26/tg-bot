module.exports = {
  apps: [{
    name: "tg-bot",
    script: "./__main__.py",
    interpreter: "/home/telebot/tg-bot/venv/bin/python3",
    autorestart: true,
  }]
}
