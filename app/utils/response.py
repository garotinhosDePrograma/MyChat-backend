from flask import jsonify

class Response:
    @staticmethod
    def success(data=None, message="Success", status_code=200):
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] =  data
        return jsonify(response), status_code

    @staticmethod
    def error(message="Error", status_code=400, errors=None):
        response = {
            'success': False,
            'message': message
        }
        if errors:
            response['errors'] = errors
        return jsonify(response), status_code

    @staticmethod
    def unauthorized(message="Unauthorized"):
        return Response.error(message, 401)
    
    @staticmethod
    def forbidden(message="Forbidden"):
        return Response.error(message, 403)
    
    @staticmethod
    def not_found(message="Not found"):
        return Response.error(message, 404)
    
    @staticmethod
    def created(data=None, message="Created successfully"):
        return Response.success(data, message, 201)