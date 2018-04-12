from flask import render_template
from app import app, db


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', title='Not Found'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html', title='Error'), 500


@app.errorhandler(403)
def forbidden_error(error):
    for item in error.description.needs:
        if item.value == 'verified':
            return render_template('403_verified.html', title='Forbidden'), 403
    return render_template('403.html', title='Forbidden'), 403
