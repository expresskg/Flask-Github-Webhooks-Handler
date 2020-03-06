from flask import Flask, render_template, request, redirect, url_for, jsonify
# http://pymotw.com/2/hmac/
import hmac
import hashlib
# http://techarena51.com/index.php/how-to-install-python-3-and-flask-on-linux/
import subprocess
import os

# https://pythonhosted.org/Flask-Mail/
from flask_mail import Mail, Message

app = Flask(__name__)

def verify_hmac_hash(data, signature):
    github_secret = bytes(os.environ['GITHUB_SECRET'], 'UTF-8')
    mac = hmac.new(github_secret, msg=data, digestmod=hashlib.sha1)
    return hmac.compare_digest('sha1=' + mac.hexdigest(), signature)

@app.route("/hook", methods=['POST'])
def github_payload():
    signature = request.headers.get('X-Hub-Signature')
    data = request.data
    if verify_hmac_hash(data, signature):
        if request.headers.get('X-GitHub-Event') == "ping":
            return jsonify({'msg': 'pong'})
        if request.headers.get('X-GitHub-Event') == "push":
            payload = request.get_json()
            if payload['commits'][0]['distinct'] == True:
                branch = payload['ref'].split('/', 2)[2]
                name = payload['repository']['name']
                try:
                    cmd_output = subprocess.check_output(
                        ['sh', '/app/hooks/' + name + '-' + branch + '.sh'])
                    return jsonify({'msg': str(cmd_output)})
                except subprocess.CalledProcessError as error:
                    return jsonify({'msg': str(error.output)})
            else:
                return jsonify({'msg': 'nothing to commit'})

    else:
        return jsonify({'msg': 'invalid hash'})


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")