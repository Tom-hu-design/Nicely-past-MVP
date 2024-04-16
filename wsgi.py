from app import app, db

if __name__ == '__main__':
    db.create_all()
    FLASK_APP=wsgi.py
    FLASK_ENV=production
    app.run(debug=True)