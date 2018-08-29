from app.blueprints import views
from app.utils.auth import requires_auth

app = views.get('hello')


@app.route('/', strict_slashes=False)
@requires_auth
def get():
    return 'Hello!'
