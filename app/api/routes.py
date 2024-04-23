from flask import Blueprint, Response, jsonify

from app.model import SkeletonApp

def generateAppBlueprint(app_instance: SkeletonApp):
    app_blueprint = Blueprint('app_blueprint', __name__)

    @app_blueprint.route('/hello_world/<string:user_name>')
    def hello_world(user_name: str) -> Response:
        result = app_instance.hello_world(user_name)
        return Response(result, status=200)
    
    @app_blueprint.route('/hello_world/get_count/<string:user_name>')
    def get_num_of_responses(user_name: str) -> Response:
        result = app_instance.get_response_count_by_user(user_name)
        response_data = {'message': f"Number of responses for {user_name}: {str(result)}"}
        return jsonify(response_data)
    
    return app_blueprint