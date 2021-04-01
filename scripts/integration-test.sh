#!/bin/bash

CONFIG_FILE="tests/config"
__config_template="
token=token of the tester bot
target_bot_id=id of your existing bot that the tester bot will interact with
channel_id=channel to use for your tests
"
function get_config {
	grep "$1" "$CONFIG_FILE" | cut -d "=" -f 2
}

if [ -z ${CI_BOT_TOKEN+x} ]; then
	CI_BOT_TOKEN=$(get_config token)
fi
if [ -z ${CI_BOT_TARGET+x} ]; then
	CI_BOT_TARGET=$(get_config target_bot_id)
fi
if [ -z ${CI_TEST_CHANNEL+x} ]; then
	CI_TEST_CHANNEL=$(get_config channel_id)
fi

if [ -z "$CI_BOT_TOKEN$CI_BOT_TARGET$CI_TEST_CHANNEL" ] && [ ! -f "$CONFIG_FILE" ]; then
	set +ex
	echo -e "\033[0;31mmaking config file, fill out ./tests/config and run this script again.\033[0m"
	echo "$__config_template" > "$CONFIG_FILE"
	exit 1
fi

pip install -r requirements-dev.txt
find tests/integration -type f -name "*.py" -print0 | xargs -0 -n 1 -I {} python3 {} "$CI_BOT_TARGET" "$CI_BOT_TOKEN" -c "$CI_TEST_CHANNEL" -r all
