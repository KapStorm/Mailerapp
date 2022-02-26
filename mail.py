from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, current_app,
)
from sendgrid.helpers.mail import *

import sendgrid


from db import get_db

bp = Blueprint('mail', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def index():
    search = request.args.get('search')
    db, c = get_db()

    if search is None:
        c.execute('SELECT * FROM email')
    else:
        c.execute('SELECT * FROM email WHERE content LIKE %s', ('%'+search+'%',))
    mails = c.fetchall()

    return render_template('mails/index.html', mails=mails)


@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        email = request.form.get('email')
        subject = request.form.get('subject')
        content = request.form.get('content')

        errors = []

        if not email:
            errors.append('Email obligatorio')
        if not subject:
            errors.append('Asunto obligatorio')
        if not content:
            errors.append('Contenido obligatorio')

        if len(errors) > 0:
            for error in errors:
                flash(error)
        else:
            send_to(email, subject, content)
            db, c = get_db()
            print(email, subject, content)
            c.execute('INSERT INTO email (email, subject, content) VALUES (%s, %s, %s)', (email, subject, content))
            db.commit()

            return redirect(url_for('mail.index'))
    return render_template('mails/create.html')


def send_to(to, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key=current_app.config['SENDGRID_KEY'])
    from_email = Email(current_app.config['FROM_EMAIL'])
    to_emai = To(to)
    content = Content('text/plain', content)
    mail = Mail(from_email, to_emai, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response)
