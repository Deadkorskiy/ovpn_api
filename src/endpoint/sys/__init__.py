from flask import Blueprint, jsonify
from src.use_cases.sys.health import HealthUseCase, HealthUseCaseRequest


sys_bp = Blueprint('sys_bp', __name__, url_prefix='/api/sys')


@sys_bp.route("/health", methods=['GET'])
def health():
    health_result = HealthUseCase().execute(HealthUseCaseRequest())
    return jsonify(health_result.value), 200 if bool(health_result.value.get('is_up', False)) else 500
