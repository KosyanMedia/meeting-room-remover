import json
import logging
import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from helpers.slack import get_new_blocks
from slack_bot.actions import remove_meeting_room, user_has_auth, update_token, get_event_info

app = App(token=os.getenv("SLACK_BOT_TOKEN"), signing_secret=os.getenv("SLACK_SIGNING_SECRET"))
api_handler = SlackRequestHandler(app)
api = FastAPI()

logging.getLogger().setLevel(logging.INFO)


def wait_for_auth(user_id, say):
    max_retry = 12
    retry_count = 0
    while retry_count < max_retry:
        if user_has_auth(user_id):
            return

        if retry_count == 0:
            say(f"Жду, пока ты авторизуешься, и начну удалять.")

        time.sleep(5)
        retry_count += 1


@app.action("cancel")
def action_button_click(body, ack, respond):
    # Acknowledge the action
    logging.info(json.dumps(body, ensure_ascii=False))
    ack()

    # Remove auth links
    response_message = {
        'text': body['message']['text'],
        'blocks': get_new_blocks(body['message']['blocks'])
    }

    respond(response_message, replace_original=True)

    user_id = body['user']['id']

    # Wait for user_auth
    wait_for_auth(user_id, respond)

    event_info = get_event_info(body['actions'])
    calendar_id, event_id = event_info["event_id"].split(":")
    result = remove_meeting_room(user_id, calendar_id, event_id)

    if result:
        respond(f"<@{user_id}> удалил переговорку из встречи :ok_hand:")
        app.client.chat_postMessage(
            channel="#meeting-rooms",
            text=f"<@{user_id}> освободил переговорку *{event_info['room']} в {event_info['time']}*"
        )


@api.post("/slack/events")
async def endpoint(req: Request):
    return await api_handler.handle(req)


@api.get('/calendar/oauth')
async def authorize(req: Request):
    # Гугл возвращает нам параметр state, который мы передаём ему
    # на самом деле это user_id
    user_id = req.query_params['state']
    auth_code = req.query_params['code']
    update_token(user_id, auth_code)
    return RedirectResponse('https://slack.com/app_redirect?app=YOUR_APP_ID_HERE')
