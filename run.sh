#/usr/bin/env bash
export PATH="/root/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
rm -rf /var/www/fixtures/output/*.xlsx
cd /var/www/fixtures && python3 /var/www/fixtures/fixtures.py
