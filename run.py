from app import app
from werkzeug.serving import run_simple


if __name__ == '__main__':
    #run_simple('localhost', 5000, app, use_reloader=True, use_debugger=True, use_evalex=True)
    app.run(host='127.0.0.1', port=3001)
