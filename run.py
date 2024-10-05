"""
This module runs the Flask application by creating an app instance 
and starting the development server.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
