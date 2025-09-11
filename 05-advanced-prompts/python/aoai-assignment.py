# Class-based implementation of the API.
# The @app.route approach is better for web applications that mix HTML pages with API endpoints, but for pure APIs, Flask-RESTful is the way to go!
#
# Note this really is NOT production ready because nothing is async!!
# Flask is not natively async supported whereas FastAPI is.

from flask import Flask, request, jsonify
from flask_restful import Api, Resource, abort, marshal_with, fields

app = Flask(__name__)

# Custom API class that wraps all responses in a data field
class DataWrappedApi(Api):
    def handle_error(self, e):
        # Let Flask-RESTful handle errors normally
        return super().handle_error(e)
    
    def output_json(self, data, code, headers=None):
        # Wrap successful responses in a data field
        if 200 <= code < 300:  # Success status codes
            wrapped_data = {'data': data}
        else:
            # Don't wrap error responses
            wrapped_data = data
        
        return jsonify(wrapped_data), code, headers

api = DataWrappedApi(app)


# Define response structures for the actual data (will be auto-wrapped in 'data' field)
hello_response_fields = {
    'message': fields.String
}

user_list_fields = {
    'users': fields.List(fields.Nested({
        'name': fields.String,
        'age': fields.Integer,
        'email': fields.String
    })),
    'total': fields.Integer
}


class HelloResource(Resource):
    
    @marshal_with(hello_response_fields)
    def get(self):
        name = request.args.get('name', 'World')
        
        # Enforce that name is a string
        if not isinstance(name, str):
            abort(400, message='name parameter must be a string')
        
        return {
            'message': f'Hello, {name}!'
        }


class DatatestResource(Resource):
    @marshal_with(user_list_fields)
    def get(self):
        # Return user data - will be automatically wrapped in 'data' field
        return {
            'users': [
                {
                    'name': 'John Doe',
                    'age': 30,
                    'email': 'john.doe@example.com'
                },
                {
                    'name': 'Jane Smith',
                    'age': 25,
                    'email': 'jane.smith@example.com'
                }
            ],
            'total': 2
        }
        

api.add_resource(HelloResource, '/hello')
api.add_resource(DatatestResource, '/datatest')

if __name__ == '__main__':
    app.run()