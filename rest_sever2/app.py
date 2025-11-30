from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import select
import json

app = Flask(__name__)
CORS(app)

def get_connection():
    return psycopg2.connect(
        dbname="app_01",
        user="postgres",
        password="tankei001",
        host="localhost",
        port="5432"
    )

def fetch_emails():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM emails ORDER BY id;")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# SSE用ジェネレーター
def event_stream():
    conn = get_connection()
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("LISTEN emails_channel;")  # チャンネルを LISTEN

    last_data = None
    while True:
        if select.select([conn],[],[],10) == ([],[],[]):  # タイムアウト10秒
            continue
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            data = fetch_emails()
            if data != last_data:
                last_data = data
                yield f"data: {json.dumps(data)}\n\n"

@app.route('/emails')
def get_emails():
    return jsonify(fetch_emails())

@app.route('/emails/stream')
def stream_emails():
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/emails', methods=['POST'])
def add_email():
    payload = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO emails (name,email) VALUES (%s,%s)",
        (payload['name'], payload['email'])
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"}), 201


##更新
@app.route('/emails/<int:id>', methods=['PUT'])
def update_email(id):
    payload = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE emails SET name=%s, email=%s WHERE id=%s",
        (payload.get('name'), payload.get('email'), id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="localhost", port=5000, threaded=True, debug=True)
