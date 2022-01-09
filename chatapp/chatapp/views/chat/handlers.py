from flask import render_template
from chatapp.views.chat import bp



@bp.route('/')
@bp.route('/client')
def client():

    return render_template('client.html')

@bp.route('/agent')
def agent():

    return render_template('agent.html')