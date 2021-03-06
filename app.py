# -*- coding: utf-8 -*-
# @Author: Japan Parikh
# @Date:   2019-02-16 15:26:12
# @Last Modified by:   Ranjit Marathay
# @Last Modified time: 2019-07-04 11:38:00


import os
import uuid
import boto3
import json
import pymysql
from datetime import datetime
from pytz import timezone

from flask import Flask, request, render_template
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_mail import Mail, Message

from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.security import generate_password_hash, \
     check_password_hash

app = Flask(__name__, template_folder='assets')
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})

app.config['MAIL_USERNAME'] = os.environ.get('EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('PASSWORD')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['DEBUG'] = True


mail = Mail(app)
api = Api(app)


db = boto3.client('dynamodb', region_name="us-west-1")
s3 = boto3.client('s3')


# aws s3 bucket where the image is stored
BUCKET_NAME = os.environ.get('MEAL_IMAGES_BUCKET')

# allowed extensions for uploading a profile photo file
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def helper_upload_meal_img(file, bucket, key):
    if file and allowed_file(file.filename):
        filename = 'https://s3-us-west-1.amazonaws.com/' \
                   + str(bucket) + '/' + str(key)
        upload_file = s3.put_object(
                            Bucket=bucket,
                            Body=file,
                            Key=key,
                            ACL='public-read',
                            ContentType='image/jpeg'
                        )
        return filename
    return None

def allowed_file(filename):
    """Checks if the file is allowed to upload"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===========================================================


def kitchenExists(kitchen_id):
    # scan to check if the kitchen name exists
    kitchen = db.scan(TableName='kitchens',
        FilterExpression='kitchen_id = :val',
        ExpressionAttributeValues={
            ':val': {'S': kitchen_id}
        }
    )

    return not kitchen.get('Items') == []

def getRdsConn():
    RDS_HOST = 'pm-mysqldb.cxjnrciilyjq.us-west-1.rds.amazonaws.com'
    RDS_PORT = 3306
    RDS_USER = 'admin'
    RDS_DB = 'pricing'
    RDS_PW = ':)'
    print("Trying to connect to RDS...")
    try:
        conn = pymysql.connect( RDS_HOST,
                                user=RDS_USER,
                                port=RDS_PORT,
                                passwd=RDS_PW,
                                db=RDS_DB)
        cur = conn.cursor()
        print("Successfully connected to RDS.")
        return [conn, cur]
    except:
        raise Exception("RDS Connection failed.")

class MealOrders(Resource):
    def post(self):
        """Collects the information of the order
           and stores it to the database.
        """
        response = {}
        data = request.get_json(force=True)
        created_at = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

        if data.get('email') == None:
            raise BadRequest('Request failed. Please provide email')
        if data.get('name') == None:
            raise BadRequest('Request failed. Please provide name')
        if data.get('street') == None:
            raise BadRequest('Request failed. Please provide street')
        if data.get('zipCode') == None:
            raise BadRequest('Request failed. Please provide zipCode')
        if data.get('city') == None:
            raise BadRequest('Request failed. Please provide city')
        if data.get('state') == None:
            raise BadRequest('Request failed. Please provide state')
        if data.get('totalAmount') == None:
            raise BadRequest('Request failed. Please provide totalAmount')
        if data.get('paid') == None:
            raise BadRequest('Request failed. Please provide paid')
        if data.get('paymentType') == None:
            raise BadRequest('Request failed. Please provide paymentType')
        if data.get('ordered_items') == None:
            raise BadRequest('Request failed. Please provide ordered_items')
        if data.get('phone') == None:
            raise BadRequest('Request failed. Please provide phone')
        if data.get('kitchen_id') == None:
            raise BadRequest('Request failed. Please provide kitchen_id')

        kitchenFound = kitchenExists(data['kitchen_id'])

        # raise exception if the kitchen does not exists
        if not kitchenFound:
            raise BadRequest('kitchen does not exist')

        order_id = data['order_id']
        totalAmount = data['totalAmount']

        order_details = []

        for i in data['ordered_items']:
            product = db.scan(TableName='meals',
                FilterExpression='meal_id = :val',
                ProjectionExpression='meal_name, price',
                ExpressionAttributeValues={
                    ':val': {'S': i['meal_id']}
                })
            item = {}
            item['meal_id'] = {}
            item['meal_id']['S'] = i['meal_id']
            item['meal_name'] = {}
            item['meal_name']['S'] = product['Items'][0]['meal_name']['S']
            item['qty'] = {}
            item['qty']['N'] = str(i['qty'])
            item['price'] = {}
            item['price']['N'] = product['Items'][0]['price']['S']
            order_details.append(item)

        order_items = [{"M": x} for x in order_details]

        try:
            add_order = db.put_item(TableName='meal_orders',
                Item={'order_id': {'S': order_id},
                      'created_at': {'S': created_at},
                      'email': {'S': data['email']},
                      'name': {'S': data['name']},
                      'street': {'S': data['street']},
                      'zipCode': {'N': str(data['zipCode'])},
                      'city': {'S': data['city']},
                      'state': {'S': data['state']},
                      'totalAmount': {'N': str(totalAmount)},
                      'paid': {'BOOL': data['paid']},
                      'status': {'S': 'open'},
                      'paymentType': {'S': data['paymentType']},
                      'order_items':{'L': order_items},
                      'phone': {'S': str(data['phone'])},
                      'kitchen_id': {'S': str(data['kitchen_id'])}
                }
            )

            kitchen = db.get_item(TableName='kitchens',
                Key={'kitchen_id': {'S': data['kitchen_id']}},
                ProjectionExpression='kitchen_name, street, city, \
                    st, phone_number, pickup_time, first_name, kitchen_id, email'
            )

            customerMsg = Message(subject='Order Confirmation',
                          sender=app.config['MAIL_USERNAME'],
                          html=render_template('emailTemplate.html',
                          order_items=order_details,
                          kitchen=kitchen['Item'],
                          totalAmount=totalAmount,
                          name=data['name']),
                          recipients=[data['email']])

            prashantMsg = Message(subject='Order Confirmation',
                          sender=app.config['MAIL_USERNAME'],
                          html=render_template('emailTemplate.html',
                          order_items=order_details,
                          kitchen=kitchen['Item'],
                          totalAmount=totalAmount,
                          name=data['name']),
                          recipients=["pmarathay@gmail.com"])

            BusinessMsg = Message(subject='Order Confirmation',
                          sender=app.config['MAIL_USERNAME'],
                          html=render_template('businessEmailTemplate.html',
                          order_items=order_details,
                          kitchen=kitchen['Item'],
                          totalAmount=totalAmount,
                          customer=data['name']),
                          recipients=[kitchen['Item']['email']['S']])

            mail.send(customerMsg)
            mail.send(BusinessMsg)

            response['message'] = 'Request successful'
            return response, 200
        except Exception as e:
            raise BadRequest('Request failed: ' + str(e))

    def get(self):
        """RETURNS ALL ORDERS PLACED TODAY"""
        response = {}
        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")

        try:
            orders = db.scan(TableName='meal_orders',
                FilterExpression='(contains(created_at, :x1))',
                ExpressionAttributeValues={
                    ':x1': {'S': todays_date}
                }
            )

            response['result'] = orders['Items']
            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. please try again later.')


class RegisterKitchen(Resource):
    def post(self):
        response = {}
        data = request.get_json(force=True)
        created_at = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

        if data.get('kitchen_name') == None \
          or data.get('description') == None \
          or data.get('email') == None \
          or data.get('username') == None \
          or data.get('password') == None \
          or data.get('first_name') == None \
          or data.get('last_name') == None \
          or data.get('street') == None \
          or data.get('city') == None \
          or data.get('st') == None \
          or data.get('zipcode') == None \
          or data.get('phone_number') == None \
          or data.get('close_time') == None \
          or data.get('open_time') == None \
          or data.get('delivery_open_time') == None \
          or data.get('delivery_close_time') == None \
          or data.get('pickup') == None \
          or data.get('delivery') == None \
          or data.get('reusable') == None \
          or data.get('disposable') == None \
          or data.get('can_cancel') == None:
            raise BadRequest('Request failed. Please provide all \
                              required information.')

        # scan to check if the kitchen name exists
        kitchen = db.scan(TableName="kitchens",
            FilterExpression='#name = :val',
            ExpressionAttributeNames={
                '#name': 'name'
            },
            ExpressionAttributeValues={
                ':val': {'S': data['name']}
            }
        )

        # raise exception if the kitchen name already exists
        if kitchen.get('Items') != []:
            response['message'] = 'This kitchen name is already taken.'
            return response, 400

        kitchen_id = uuid.uuid4().hex

        can_cancel = False
        if data['can_cancel'] == 'true':
          can_cancel = True

        try:
            add_kitchen = db.put_item(TableName='kitchens',
                Item={'kitchen_id': {'S': kitchen_id},
                      'created_at': {'S': created_at},
                      'kitchen_name': {'S': data['kitchen_name']},
                      'description': {'S': data['description']},
                      'username': {'S': data['username']},
                      'password': {'S': generate_password_hash(data['password'])},
                      'first_name': {'S': data['first_name']},
                      'last_name': {'S': data['last_name']},
                      'street': {'S': data['street']},
                      'city': {'S': data['city']},
                      'st': {'S': data['st']},
                      'zipcode': {'N': str(data['zipcode'])},
                      'phone_number': {'S': str(data['phone_number'])},
                      'open_time': {'S': str(data['open_time'])},
                      'close_time': {'S': str(data['close_time'])},
                      'isOpen': {'BOOL': False},
                      'email': {'S': data['email']},
                      'delivery_open_time': { 'S': data['delivery_open_time' ]},
                      'delivery_close_time': { 'S': data['delivery_close_time' ]},
                      'pickup': { 'BOOL': data['pickup']},
                      'delivery': { 'BOOL': data['delivery']},
                      'reusable': { 'BOOL': data['reusable']},
                      'disposable': { 'BOOL': data['disposable']},
                      'can_cancel': { 'BOOL': can_cancel}
                }
            )

            response['message'] = 'Request successful'
            response['kitchen_id'] = kitchen_id
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')


def formateTime(time):
    hours = time.rsplit(':', 1)[0]
    mins = time.rsplit(':', 1)[1]
    if hours == '00':
        return '{}:{} AM'.format('12', mins)
    elif hours >= '12' and hours < '24':
        if hours == '12':
            return '{}:{} PM'.format(hours, mins)
        return '{}:{} PM'.format((int(hours) - 12), mins)
    else:
        return '{}:{} AM'.format(hours, mins)

class Kitchens(Resource):
    def get(self):
        """Returns all kitchens"""
        response = {}

        try:
            kitchens = db.scan(TableName='kitchens',
                ProjectionExpression='kitchen_name, kitchen_id, \
                    close_time, description, open_time, isOpen, \
                    accepting_hours, is_accepting_24hr, delivery_hours',
            )

            result = []

            for kitchen in kitchens['Items']:
                kitchen['open_time']['S'] = formateTime(kitchen['open_time']['S'])
                kitchen['close_time']['S'] = formateTime(kitchen['close_time']['S'])

                if kitchen['isOpen']['BOOL'] == True:
                    result.insert(0, kitchen)
                else:
                    result.append(kitchen)

            response['message'] = 'Request successful'
            response['result'] = result
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')


class Kitchen(Resource):
    def get(self, kitchen_id):
        kitchen = db.scan(TableName='kitchens',
            FilterExpression='kitchen_id = :val',
            ExpressionAttributeValues={
                ':val': {'S': kitchen_id}
            }
        )
        if (kitchen.get('Items') == []):
            return "Kitchen not found.", 404
        return kitchen, 200

    def put(self, kitchen_id):
        """ Updates kitchen information.
        Since the UI infers that a Kitchen is actually three Resources (User, Home, Kitchen),
        this method allows updates for specific Resources through the use of a 'type' key,
        which indicates which Resource is being updated.
        """
        if not kitchenExists(kitchen_id):
            return BadRequest('Kitchen could not be found.')

        response = {}
        data = request.get_json(force=True)
        if ('type' not in data):
            raise BadRequest('Missing update type.')
        if ('payload' not in data):
            raise BadRequest('Missing payload.')

        REGISTRATION_FIELD_KEYS = [
          'username',
          'password'
        ]
        PERSONAL_FIELD_KEYS = [
          'first_name',
          'last_name',
          'street',
          'city',
          'st',
          'zipcode',
          'phone_number',
          'email'
        ]
        KITCHEN_FIELD_KEYS = [
          'kitchen_name',
          'description',
          'open_time',
          'close_time',
          'delivery_option',
          'container_option',
          'cancellation_option'
        ]
        def findMissingFieldKey(fields, payload):
            """Finds the first missing field in payload.
            Returns first field in fields that is not in payload, or None if all fields are in payload.
            """
            for i in range(len(fields)):
                if fields[i] not in payload:
                    return fields[i]
            return None
        payload = data['payload']
        if (data['type'] == 'registration'):
            missing_field = findMissingFieldKey(REGISTRATION_FIELD_KEYS, payload)
            if (missing_field == None):
                try:
                    db.update_item(TableName='kitchens',
                        Key={'kitchen_id': {'S': str(kitchen_id)}},
                        UpdateExpression='SET username = :un, passsword = :pw',
                        ExpressionAttributeValues={
                            ':un': {'S': payload['username']},
                            ':pw': {'S': generate_password_hash(payload['password'])}
                        }
                    )
                    response['message'] = 'Update successful'
                    return response, 200
                except:
                    raise BadRequest('Request failed. Please try again later.')
            else:
                return BadRequest('Missing field: ' + missing_field)
        elif (data['type'] == 'personal'):
            missing_field = findMissingFieldKey(PERSONAL_FIELD_KEYS, payload)
            if (missing_field == None):
                try:
                    db.update_item(TableName='kitchens',
                        Key={'kitchen_id': {'S': str(kitchen_id)}},
                        UpdateExpression='SET first_name = :fn, last_name = :ln, street = :a, city = :c, #state = :s, zipcode = :z, phone_number = :pn, email = :e',
                        ExpressionAttributeNames={
                          '#state': 'state'
                        },
                        ExpressionAttributeValues={
                            ':fn': {'S': payload['first_name']},
                            ':ln': {'S': payload['last_name']},
                            ':a': {'S': payload['address']},
                            ':c': {'S': payload['city']},
                            ':s': {'S': payload['state']},
                            ':z': {'N': str(payload['zipcode'])},
                            ':pn': {'S': str(payload['phone_number'])},
                            ':e': {'S': payload['email']}
                        }
                    )
                    response['message'] = 'Update successful'
                    return response, 200
                except:
                    raise BadRequest('Request failed. Please try again later.')
            else:
                return BadRequest('Missing field: ' + missing_field)
        elif (data['type'] == 'kitchen'):
            missing_field = findMissingFieldKey(KITCHEN_FIELD_KEYS, payload)
            if (missing_field == None):
                try:
                    db.update_item(TableName='kitchens',
                        Key={'kitchen_id': {'S': str(kitchen_id)}},
                        UpdateExpression='SET #name = :n, description = :d, open_time = :ot, close_time = :ct, delivery_option = :do, container_option = :co, cancellation_option = :cao',
                        ExpressionAttributeNames={
                            '#name': 'name'
                        },
                        ExpressionAttributeValues={
                            ':n': {'S': payload['name']},
                            ':d': {'S': payload['description']},
                            ':ot': {'S': payload['open_time']},
                            ':ct': {'S': payload['close_time']},
                            ':do': {'S': payload['delivery_option']},
                            ':co': {'S': str(payload['container_option'])},
                            ':cao': {'S': str(payload['cancellation_option'])}
                        }
                    )
                    response['message'] = 'Update successful'
                    return response, 200
                except:
                    raise BadRequest('Request failed. Please try again later.')
            else:
                return BadRequest('Missing field: ' + missing_field)
        else:
            return BadRequest('\'type\' must have one of the following values: \'registration\', \'personal\', \'kitchen\'')


class Meals(Resource):
    def post(self, kitchen_id):
        response = {}

        kitchenFound = kitchenExists(kitchen_id)

        # raise exception if the kitchen does not exists
        if not kitchenFound:
            raise BadRequest('kitchen does not exist')

        if request.form.get('name') == None \
          or request.form.get('items') == None \
          or request.form.get('price') == None:
            raise BadRequest('Request failed. Please provide required details.')

        meal_id = uuid.uuid4().hex
        created_at = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%dT%H:%M:%S")

        meal_items = json.loads(request.form['items'])

        items = []
        for i in meal_items['meal_items']:
            item = {}
            item['title'] = {}
            item['title']['S'] = i['title']
            item['qty'] = {}
            item['qty']['N'] = str(i['qty'])
            items.append(item)

        description = [{'M': i} for i in items]

        try:
            photo_key = 'meals_imgs/{}_{}'.format(str(kitchen_id), str(meal_id))
            photo_path = helper_upload_meal_img(request.files['photo'], BUCKET_NAME, photo_key)

            if photo_path == None:
                raise BadRequest('Request failed. \
                    Something went wrong uploading a photo.')

            add_meal = db.put_item(TableName='meals',
                Item={'meal_id': {'S': meal_id},
                      'created_at': {'S': created_at},
                      'kitchen_id': {'S': str(kitchen_id)},
                      'meal_name': {'S': str(request.form['name'])},
                      'description': {'L': description},
                      'price': {'S': str(request.form['price'])},
                      'photo': {'S': photo_path}
                }
            )

            kitchen = db.update_item(TableName='kitchens',
                Key={'kitchen_id': {'S': str(kitchen_id)}},
                UpdateExpression='SET isOpen = :val',
                ExpressionAttributeValues={
                    ':val': {'BOOL': True}
                }
            )

            response['message'] = 'Request successful'
            return response, 201
        except:
            raise BadRequest('Request failed. Please try again later.')

    def get(self, kitchen_id):
        response = {}

        print(kitchen_id)

        kitchenFound = kitchenExists(kitchen_id)

        # raise exception if the kitchen does not exists
        if not kitchenFound:
            raise BadRequest('kitchen does not exist')

        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")

        try:
            # meals = db.scan(TableName='meals',
            #     FilterExpression='kitchen_id = :value and (contains(created_at, :x1))',
            #     ExpressionAttributeValues={
            #         ':value': {'S': kitchen_id},
            #         ':x1': {'S': todays_date}
            #     }
            # )

            print("kitchen meal scan start")
            meals = db.scan(TableName='meals',
                FilterExpression='kitchen_id = :value',
                ExpressionAttributeValues={
                    ':value': {'S': kitchen_id}
                }
            )
            print("kitchen meal scan finish")


            for meal in meals['Items']:
                description = ''

                for item in meal['description']['L']:
                    if int(item['M']['qty']['N']) > 1:
                        description = description + item['M']['qty']['N'] + ' ' \
                                     + item['M']['title']['S'] + ', '
                    else:
                        description = description + item['M']['title']['S'] + ', '

                del meal['description']
                meal['description'] = {}
                meal['description']['S'] = description[:-2]

            response['message'] = 'Request successful!'
            response['result'] = meals['Items']
            return response, 200
        except:
            raise BadRequest('Request failed. Please try again later.')


class OrderReport(Resource):
    def get(self, kitchen_id):
        response = {}

        kitchenFound = kitchenExists(kitchen_id)

        # raise exception if the kitchen does not exists
        if not kitchenFound:
            raise BadRequest('kitchen does not exist')

        todays_date = datetime.now(tz=timezone('US/Pacific')).strftime("%Y-%m-%d")
        k_id = kitchen_id

        try:
            orders = db.scan(TableName='meal_orders',
                FilterExpression='kitchen_id = :value AND (contains(created_at, :x1))',
                ExpressionAttributeValues={
                    ':value': {'S': k_id},
                    ':x1': {'S': todays_date}
                }
            )

            response['result'] = orders['Items']
            response['message'] = 'Request successful'
            return response, 200
        except:
            raise BadRequest('Request failed. please try again later.')

class LatestPricing(Resource):
    def get(self):
        response = {}
        try:
            # Connect to RDS
            rds = getRdsConn()
            conn = rds[0]
            cur = rds[1]

            # Run query
            query = """ SELECT item, price, unit, store, zipcode, max(price_date) as \'latestDate\'
                        FROM groceries
                        GROUP BY item, store, zipcode;"""
            cur.execute(query)
            queriedData = cur.fetchall()

            # Write queried data to json
            items = []
            for row in queriedData:
                rowDict = {}
                rowDictKeys = ('item', 'price', 'unit', 'store', 'zipcode', 'latestDate')
                
                for element in enumerate(row):
                    keyToAppend = rowDictKeys[element[0]]
                    valueToAppend = element[1]
                    if keyToAppend == 'price':
                        valueToAppend = float(valueToAppend)
                    rowDict[keyToAppend] = valueToAppend
                items.append(rowDict)

            response['message'] = 'Request successful.'
            response['result'] = items

            # Close RDS connection
            cur.close()
            conn.close()
            return response, 200
        except:
            raise BadRequest('Request failed, please try again later.')

api.add_resource(MealOrders, '/api/v1/orders')
# api.add_resource(TodaysMealPhoto, '/api/v1/meal/image/upload')
api.add_resource(RegisterKitchen, '/api/v1/kitchens/register')
api.add_resource(Meals, '/api/v1/meals/<string:kitchen_id>')
api.add_resource(OrderReport, '/api/v1/orders/report/<string:kitchen_id>')
api.add_resource(Kitchens, '/api/v1/kitchens')
api.add_resource(Kitchen, '/api/v1/kitchen/<string:kitchen_id>')
api.add_resource(LatestPricing, '/api/v1/latestpricing')

if __name__ == '__main__':
    app.run(host='localhost', port='5000')
