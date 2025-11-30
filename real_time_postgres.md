
create table emails (
id SERIAL,
name text,
email text,
primary key(id)
 ) ;




-- 通知用関数
CREATE OR REPLACE FUNCTION notify_email_change()
RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify('emails_channel', 'update');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- トリガー設定
CREATE TRIGGER emails_notify_trigger
AFTER INSERT OR UPDATE ON emails
FOR EACH ROW EXECUTE FUNCTION notify_email_change();