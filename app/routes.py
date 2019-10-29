from app import app


@app.route('/')
@app.route('/index')
@app.route('/search')
def index():
	return 'frontpage working!'
