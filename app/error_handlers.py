"""
Custom error handlers with detailed debugging information
"""
from flask import render_template, request, current_app
import traceback
import sys
from datetime import datetime

def register_error_handlers(app):
    """Register custom error handlers with detailed debugging info"""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        error_details = {
            'error_code': 400,
            'error_type': 'Bad Request',
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'request_url': request.url,
            'request_method': request.method,
            'request_headers': dict(request.headers),
            'request_form': dict(request.form) if request.form else None,
            'request_args': dict(request.args) if request.args else None,
            'user_agent': request.user_agent.string,
            'remote_addr': request.remote_addr,
            'traceback': traceback.format_exc() if current_app.debug else None
        }
        
        # Log the detailed error
        current_app.logger.error(f"400 Bad Request Error: {error_details}")
        
        return render_template('error.html', error_details=error_details), 400
    
    @app.errorhandler(401)
    def unauthorized_error(error):
        error_details = {
            'error_code': 401,
            'error_type': 'Unauthorized',
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'request_url': request.url,
            'request_method': request.method,
            'user_agent': request.user_agent.string,
            'remote_addr': request.remote_addr,
        }
        
        current_app.logger.error(f"401 Unauthorized Error: {error_details}")
        
        return render_template('error.html', error_details=error_details), 401
    
    @app.errorhandler(403)
    def forbidden_error(error):
        error_details = {
            'error_code': 403,
            'error_type': 'Forbidden',
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'request_url': request.url,
            'request_method': request.method,
            'user_agent': request.user_agent.string,
            'remote_addr': request.remote_addr,
        }
        
        current_app.logger.error(f"403 Forbidden Error: {error_details}")
        
        return render_template('error.html', error_details=error_details), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        error_details = {
            'error_code': 404,
            'error_type': 'Not Found',
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'request_url': request.url,
            'request_method': request.method,
            'user_agent': request.user_agent.string,
            'remote_addr': request.remote_addr,
        }
        
        current_app.logger.error(f"404 Not Found Error: {error_details}")
        
        return render_template('error.html', error_details=error_details), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        error_details = {
            'error_code': 500,
            'error_type': 'Internal Server Error',
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'request_url': request.url,
            'request_method': request.method,
            'request_headers': dict(request.headers),
            'request_form': dict(request.form) if request.form else None,
            'request_args': dict(request.args) if request.args else None,
            'user_agent': request.user_agent.string,
            'remote_addr': request.remote_addr,
            'traceback': traceback.format_exc() if current_app.debug else None
        }
        
        current_app.logger.error(f"500 Internal Server Error: {error_details}")
        
        return render_template('error.html', error_details=error_details), 500