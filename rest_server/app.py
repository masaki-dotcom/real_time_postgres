from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import psycopg2
import select
import atexit
import json
import threading
import queue
import psycopg2.extras

app = Flask(__name__)
# CORS(app)  # ←これで全てのオリジンからアクセス可能
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


# --- DB接続（API用） ---
api_conn = psycopg2.connect("dbname=app_01 user=postgres password=tankei001 host=localhost")
api_conn.autocommit = True

# --- DB接続（SSE用 LISTEN専用） ---
listen_conn = psycopg2.connect("dbname=app_01 user=postgres password=tankei001 host=localhost")
listen_conn.autocommit = True

listen_cur = listen_conn.cursor()
listen_cur.execute("LISTEN users_events;")

# SSE用キュー
event_queue = queue.Queue()



# -------------------------------
# SSE 用ジェネレーター
# -------------------------------

# PostgreSQL LISTEN をバックグラウンドで待機するスレッド
# LISTENスレッド
def listen_notify():
    while True:
        if select.select([listen_conn], [], [], 5) == ([], [], []):
            continue
        listen_conn.poll()
        while listen_conn.notifies:
            notify = listen_conn.notifies.pop(0)
            print("🔔 Notify received:", notify.payload)
            event_queue.put(notify.payload)

thread = threading.Thread(target=listen_notify, daemon=True)
thread.start()


# SSE エンドポイント
@app.get("/events")
def sse_stream():
    def event_stream():
        while True:
            # 通知が来るまでブロック（待機）
            payload = event_queue.get()   # timeoutなしです
            yield f"data: {payload}\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "text/event-stream",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    }

    return Response(event_stream(), headers=headers)

# ===== REST API =====

@app.get("/users/<int:id>")
def get_user(id):
    cur = api_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE id=%s", (id,))
    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(row)

@app.get("/users")
def get_users():
    cur = api_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows)


@app.post("/users")
def create_user():
    data = request.json
    cur = api_conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
        (data["name"], data["email"])
    )
    new_id = cur.fetchone()[0]
    cur.close()
    return jsonify({"id": new_id})


@app.put("/users/<int:id>")
def update_user(id):
    data = request.json
    cur = api_conn.cursor()
    cur.execute(
        "UPDATE users SET name=%s, email=%s WHERE id=%s",
        (data["name"], data["email"], id)
    )
    cur.close()
    return jsonify({"status": "ok"})


# -------------------------------
# アプリ終了時に接続を閉じる
# -------------------------------
def cleanup():
    print("Closing PostgreSQL connections...")

    # API 用接続
    try:      
        api_conn.close()
        print("API connection closed")
    except Exception as e:
        print("Error closing API connection:", e)

    # SSE 用接続
    try:
        listen_cur.close()
        listen_conn.close()
        print("SSE connection closed")
    except Exception as e:
        print("Error closing SSE connection:", e)

atexit.register(cleanup)

if __name__ == "__main__":
    app.run(host="localhost", port=5001, threaded=True, debug=True)
