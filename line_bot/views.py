import datetime
import os
import logging

import pydantic

from line_bot.utils.template_builder import TemplateBuilder
from line_bot.utils.postback import QuestionPostback
from question_bank.exception import CategoryNotFoundError, SubjectNotFoundError

from django import http
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    StickerMessage,
    FlexCarousel,
)
from linebot.v3.webhooks import (
    MessageEvent,
    PostbackEvent,
    TextMessageContent
)


configuration = Configuration(access_token=os.getenv("LINE_MESSAGE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_MESSAGE_CHANNEL_SECRET"))

logger = logging.getLogger('line_bot')

# Create your views here.
@csrf_exempt 
def callback(request):
    if request.method == 'POST':
        try:
            # get X-Line-Signature header value
            signature = request.headers['X-Line-Signature']

            # get request body as text
            body = request.body.decode('utf-8')

            # handle webhook body
            handler.handle(body, signature)
        except (InvalidSignatureError, KeyError):
            return http.HttpResponseBadRequest("Invalid signature. Please check your channel access token/channel secret.")

        return http.HttpResponse("OK")
    else:
        return http.HttpResponseNotAllowed(["POST"])

@handler.add(PostbackEvent)
def handle_postback_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        try:
            user_profile = line_bot_api.get_profile(event.source.user_id)
            postback = QuestionPostback(user_profile, event.postback.data)

            logger.debug("=== Handling Line Postback Event ===")
            logger.debug("Time: %s", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            logger.debug("Line User ID: %s", user_profile.user_id)
            logger.debug("Display Name: %s", user_profile.display_name)
            logger.debug(f"Postback Data: {event.postback.data}")
            logger.debug("Data Size: %d/300", len(event.postback.data))
            logger.debug("====================================")

            match postback.flag:
                case QuestionPostback.PostbackFlag.SELECT_CATEGORY:
                    message = TemplateBuilder.select_category()
                case QuestionPostback.PostbackFlag.SELECT_SUBJECT:
                    message = TemplateBuilder.select_subject(postback)
                case QuestionPostback.PostbackFlag.SELECT_MODE:
                    message = TemplateBuilder.select_mode(postback)
                case QuestionPostback.PostbackFlag.QUESTION:
                    message = TemplateBuilder.question(postback)
                case QuestionPostback.PostbackFlag.QUESTION_REVIEW:
                    message = TemplateBuilder.question_review(postback)
                case _:
                    raise ValueError('Unknown message action flag: {}'.format(postback.flag))
            
            reply_message = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=message if isinstance(message, list) else [message]
            )
            error_message = None

            line_bot_api.reply_message(reply_message)

        except (CategoryNotFoundError, SubjectNotFoundError) as e:
            logger.exception("Failed to build Line flex message template due to missing category or subject: %s", e)
            error_message = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text='類科或科目遭到變更或移除'), 
                    StickerMessage(package_id='11537', sticker_id='52002749')
                ]
            )

        except pydantic.ValidationError as e:
            logger.exception("Error building Line flex message template: %s", e)
            error_message = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text='訊息建構錯誤'),
                    StickerMessage(package_id='11537', sticker_id='52002749')
                ]
            )

        except Exception as e:
            logger.exception("Handling Line Postback Event Error: %s", e)
            error_message = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text='發生其他問題'), 
                    StickerMessage(package_id='11537', sticker_id='52002770')
                ]
            )

        finally:
            if error_message:
                line_bot_api.reply_message(error_message)

        return http.HttpResponse("OK")


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        
        if event.message.text == "題庫":
            try:
                messages = [TemplateBuilder.select_category()]

            except pydantic.ValidationError as e:
                logger.exception("Error building Line flex message template: %s", e)
                messages=[
                    TextMessage(text='訊息建構錯誤'),
                    StickerMessage(package_id='11537', sticker_id='52002749')
                ]

            except Exception as ex:
                messages=[
                    TextMessage(text='發生其他問題'), 
                    StickerMessage(package_id='11537', sticker_id='52002770')
                ]

            finally:
                line_bot_api.reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=messages
                    )
                )
        else:
            # 其他訊息
            pass