import os
import sys
import json

import requests
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return render_template('home.html'), 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    #send_message(sender_id, "Hi, I'm your personal BOT. I can do a lot of things for you. but for now just ask me my name")
                    add_greeting(sender_id, message_text)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200

def add_greeting(sender_id, message_text):
    if "hi" in message_text:
        send_message(sender_id, "Hello I'm a Bot")
    else:
        send_message(sender_id, "Errr, I don't get it")

def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
      "recipient":{
        "id": recipient_id
      },
      "message":{
        "attachment":{
          "type":"template",
          "payload":{
            "template_type":"receipt",
            "recipient_name":"Khizar Naeem",
            "order_number":"12345678902",
            "currency":"EUR",
            "payment_method":"iDeal",
            "order_url":"http://debijenkorf.nl",
            "timestamp":"1428444852",
            "elements":[
              {
                "title":"Maine3 regular fit jeans van stretchkatoen",
                "subtitle":"HUGO BOSS",
                "quantity":1,
                "price":139.95,
                "currency":"EUR",
                "image_url":"https://cdn-1.debijenkorf.nl/web_detail_2x/hugo-boss-maine3-regular-fit-jeans-van-stretchkatoen/?reference=092/880/13_0928801007700000_pro_mod_frt_01_1108_1528_1284735.jpg"
              },
              {
                "title":"Daisley T-shirt met paisleyprint",
                "subtitle":"HUGO BOSS",
                "quantity":1,
                "price":48.95,
                "currency":"EUR",
                "image_url":"https://cdn-1.debijenkorf.nl/web_detail_2x/hugo-boss-daisley-t-shirt-met-paisleyprint/?reference=045/310/13_0453103910700000_pro_mod_frt_01_1108_1528_1220614.jpg"
              }
            ],
            "address":{
              "street_1":"Dam 1",
              "street_2":"",
              "city":"Amsterdam",
              "postal_code":"1012 JS",
              "state":"NH",
              "country":"NL"
            },
            "summary":{
              "subtotal":188.90,
              "shipping_cost":3.95,
              "total_tax":0,
              "total_cost":188.90
            },
            "adjustments":[
              {
                "name":"New Customer Discount",
                "amount":10
              },
              {
                "name":"$10 Off Coupon",
                "amount":10
              }
            ]
          }
        }
      }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
