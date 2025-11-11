from flask import Blueprint, jsonify, render_template
from services.library_service import get_patron_status_report

#MY API ATTEMPT No.4!
patron_bp = Blueprint('patron', __name__)

@patron_bp.route('/patron/status')
def patron_status_page():
    """create the patron status page."""
    return render_template('patron_status.html')

@patron_bp.route('/api/patron/<patron_id>/status', methods=['GET'])
def get_patron_status(patron_id):
    """
    Get status information for a patron including:
    - Currently borrowed books
    - Total late fees
    - Number of overdue books
    """
    status = get_patron_status_report(patron_id) # run this function from library_service
    return jsonify(status)