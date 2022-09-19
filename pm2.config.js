module.exports = {
  apps: [{
    name: "tg-bot",
    script: "./__main__.py",
    interpreter: "/home/tg-bot/.env/bin/python3",
    autorestart: true,
  }]
}
