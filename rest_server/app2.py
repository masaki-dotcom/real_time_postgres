from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from flask_restful import Api, Resource
import psycopg2
from psycopg2.extras import RealDictCursor
import select
import json

app = Flask(__name__)
CORS(app)
api = Api(app)

# DB接続
def get_connection():
    return psycopg2.connect(
        dbname="app_01",
        user="postgres",
        password="tankei001",
        host="localhost",
        port="5432"
    )

# emails 全件取得
def fetch_emails():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM emails ORDER BY id;")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


# ---------------------------
#   SSE イベントストリーム
# ---------------------------
def event_stream():
    conn = get_connection()
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("LISTEN emails_channel;") # チャンネルを LISTEN

    last_data = None

    while True:
        if select.select([conn], [], [], 10) == ([], [], []): # タイムアウト10秒
            continue

        conn.poll()

        while conn.notifies:
            notify = conn.notifies.pop(0)

            data = fetch_emails()
            if data != last_data:
                last_data = data
                yield f"data: {json.dumps(data)}\n\n"

# ---------------------------
#       Resource クラス
# ---------------------------

# 一覧 + 新規作成
class Emails(Resource):
    def get(self):
        """GET /emails"""
        return jsonify(fetch_emails())

    def post(self):
        """POST /emails"""
        payload = request.json
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO emails (name, email) VALUES (%s, %s)",
            (payload['name'], payload['email'])
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok"}, 201


# 個別更新・削除
class EmailItem(Resource):
    def put(self, id):
        """PUT /emails/<id>"""
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
    def delete(self, id):
        """DELETE /emails/<id>"""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM emails WHERE id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})

# SSEストリーム
class EmailsStream(Resource):
    def get(self):
        """GET /emails/stream"""
        return Response(event_stream(), mimetype="text/event-stream") 
        #mimetype="text/event-stream" ⇒ SSE（Server-Sent Events）用のストリーム
        ##片方向のリアルタイム通信 を継続的に送りつづける機能 これを付けないとリアルタイムで受信されない


# ---------------------------
#   URL Mapping
# ---------------------------
api.add_resource(Emails, "/emails")
api.add_resource(EmailItem, "/emails/<int:id>")
api.add_resource(EmailsStream, "/emails/stream")

# ---------------------------
#      メイン実行
# ---------------------------
if __name__ == "__main__":
    app.run(host="localhost", port=5000, threaded=True, debug=True)
