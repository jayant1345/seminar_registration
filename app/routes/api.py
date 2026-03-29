"""REST API endpoints (bonus feature)."""
from flask import Blueprint, current_app, jsonify, request

from app.models import Participant

api_bp = Blueprint('api', __name__)


@api_bp.route('/registrations', methods=['GET'])
def get_registrations():
    """GET /api/v1/registrations — paginated list of all registrations."""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    pagination = (Participant.query
                  .order_by(Participant.timestamp.desc())
                  .paginate(page=page, per_page=per_page, error_out=False))

    return jsonify({
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': per_page,
        'registrations': [p.to_dict() for p in pagination.items],
    })


@api_bp.route('/registrations/<string:reg_id>', methods=['GET'])
def get_registration(reg_id: str):
    """GET /api/v1/registrations/<reg_id> — single registration lookup."""
    participant = Participant.query.filter_by(
        registration_id=reg_id).first_or_404()
    return jsonify(participant.to_dict())


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """GET /api/v1/stats — registration statistics per seminar."""
    seminars = current_app.config['SEMINARS']
    by_seminar = {
        s: Participant.query.filter_by(seminar=s).count()
        for s in seminars
    }
    return jsonify({
        'total_registrations': Participant.query.count(),
        'by_seminar': by_seminar,
    })
