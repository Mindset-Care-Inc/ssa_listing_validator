from flask import Blueprint, Response, jsonify, render_template, request

from app.model import SkeletonApp

def generateAppBlueprint(app_instance: SkeletonApp):
    app_blueprint = Blueprint('app_blueprint', __name__)

    @app_blueprint.route('/')
    def index() -> Response:
        return render_template('index.html', intro_question="Hello, How can I help you?")
    
    @app_blueprint.route('/search_websites', methods=['POST'])
    def search_websites() -> Response:
        user_input = request.form['prompt']
        result = app_instance.search_websites(user_input)
        return jsonify({'answer':result[0],'Citations':result[1]}), 200
        
    
    @app_blueprint.route('/hello_world/<string:user_name>')
    def hello_world(user_name: str) -> Response:
        result = app_instance.hello_world(user_name)
        return Response(result, status=200)

    @app_blueprint.route('/submit_user_feedback', methods=['POST'])
    def submit_user_feedback() -> Response:
        question = request.form['question']
        answer = request.form['answer']
        feedback =request.form['feedback']
        result = app_instance.store_user_feedback(question, answer,feedback)
        return jsonify(result), 200
    
    @app_blueprint.route('/hello_world/get_count/<string:user_name>')
    def get_num_of_responses(user_name: str) -> Response:
        result = app_instance.get_response_count_by_user(user_name)
        response_data = {'message': f"Number of responses for {user_name}: {str(result)}"}
        return jsonify(response_data)
    
    return app_blueprint