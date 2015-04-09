from flask import Flask, session, request, render_template, redirect, Response
import uuid
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
from os import urandom


app = Flask(__name__)
app.secret_key = urandom(24)


def generate_ticket(service):
    url = urlparse(service)
    query = parse_qs(url.query)
    query.update({'ticket': "%s-%s" % (session["username"], str(uuid.uuid1()))})
    payload = urlencode(query)
    return redirect("%s://%s%s?%s" % (url.scheme, url.netloc, url.path, payload))


@app.route('/login')
def login():
    service = request.args.get('service')
    print(service)
    if 'username' not in session:
        return render_template('login.html', **locals())
    else:
        return generate_ticket(service)
       
 
@app.route('/auth')
def auth():
    service = request.args.get('service')
    session['username'] = request.args.get('username')
    return generate_ticket(service)


@app.route('/serviceValidate')
def validate():
    session['logged'] = True
    username = request.args.get('ticket').split("-")[0]
    return Response("""<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'><cas:authenticationSuccess><cas:user>%s</cas:user></cas:authenticationSuccess></cas:serviceResponse>""" % username, mimetype='text/xml')


@app.route('/logout')
def logout():
    del session['logged']
    return redirect(request.args.get('url'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
