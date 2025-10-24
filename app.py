# app.py
from flask import Flask, request, render_template, redirect
import sqlite3, datetime, os

app = Flask(__name__)
DB = 'sim.db'

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        conn.execute('CREATE TABLE events (id INTEGER PRIMARY KEY, event TEXT, info TEXT, ts TEXT)')
        conn.commit()
        conn.close()

def log(event, info=""):
    conn = sqlite3.connect(DB)
    conn.execute('INSERT INTO events (event, info, ts) VALUES (?,?,?)',
                 (event, info, datetime.datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    # shows the fake email body
    return render_template('email_template.html')

@app.route('/phish_link')
def phish_link():
    ua = request.headers.get('User-Agent','')
    ip = request.remote_addr
    log('click', f'ip={ip};ua={ua}')
    return redirect('/landing')

@app.route('/landing', methods=['GET','POST'])
def landing():
    if request.method == 'POST':
        credential = request.form.get('username','') + '|' + request.form.get('password','')
        log('submit', f'creds={credential}')
        return render_template('awareness.html', submitted=True)
    return render_template('landing.html', submitted=False)

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB)
    cur = conn.execute('SELECT event, COUNT(*) FROM events GROUP BY event')
    rows = cur.fetchall()
    conn.close()
    return render_template('dashboard.html', rows=rows)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
