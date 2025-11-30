
## SSE(SSE = Server-Sent Events: サーバー送信イベント)
`サーバー → ブラウザ へ一方通行でリアルタイム通知を送る仕組み`


### なにができるのか？
- データが変わったら 自動でフロントに通知 できる
- フロント側は イベントストリームを受け取って UI を更新できる
- WebSocketよりも設定がシンプルで、サーバーからの通知だけなら SSE のほうが楽！

### 具体例 Nuxt3 + Flask + PostgreSQL の構成だと…
1. PostgreSQL で行が INSERT / UPDATE / DELETE される
1. トリガーで pg_notify() が呼ばれる
1. Flask が LISTEN して受け取る
1. Flask が SSE で Nuxt3 に通知する
1. Nuxt3 が自動更新する

### PostgreSQLの設定
```
create table emails (
id SERIAL,
name text,
email text,
primary key(id)
 ) ;

```

```
-- 通知用関数
CREATE OR REPLACE FUNCTION notify_email_change()
RETURNS trigger AS $$
BEGIN
  PERFORM pg_notify('emails_channel', TG_OP);
  IF (TG_OP = 'DELETE') THEN
    RETURN OLD;
  ELSE
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;


-- トリガー設定
CREATE TRIGGER emails_notify_trigger
AFTER INSERT OR UPDATE OR DELETE ON emails
FOR EACH ROW EXECUTE FUNCTION notify_email_change();
```  

```
--- 既に存在するトリガーを削除する場合
DROP TRIGGER IF EXISTS emails_notify_trigger ON emails;
```  


　　
