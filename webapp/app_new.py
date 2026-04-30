import os
import sys
import logging
from flask import Flask
from flask_cors import CORS

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('chess_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)

app.logger.setLevel(logging.INFO)
for handler in logging.getLogger().handlers:
    app.logger.addHandler(handler)

@app.before_request
def log_request():
    from flask import request
    if request.path.startswith('/api/'):
        try:
            json_data = request.get_json(silent=True)
            logger.info(f"收到API请求: {request.method} {request.path}", extra={
                'method': request.method,
                'path': request.path,
                'args': request.args.to_dict(),
                'json': json_data
            })
        except Exception as e:
            logger.info(f"收到API请求: {request.method} {request.path}")

@app.after_request
def log_response(response):
    from flask import request
    if request.path.startswith('/api/'):
        logger.info(f"API响应: {request.method} {request.path} -> {response.status_code}")
    return response

from config.settings import init_directories
init_directories()

from routes.analysis_routes import analysis_bp
from routes.player_routes import player_bp
from routes.game_routes import game_bp
from routes.exercise_routes import exercise_bp
from routes.profile_routes import profile_bp
from routes.train_plan_routes import train_plan_bp
from routes.token_routes import token_bp

app.register_blueprint(analysis_bp)
app.register_blueprint(player_bp)
app.register_blueprint(game_bp)
app.register_blueprint(exercise_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(train_plan_bp)
app.register_blueprint(token_bp)

from config.settings import OUTPUT_DIR, LIBRARY_DIR, PROFILE_DIR, PLAN_DIR, PLAYERS_DIR, EXERCISES_DIR

if __name__ == '__main__':
    logger.info(f"目录初始化完成")
    app.run(debug=True, host='0.0.0.0', port=5000)