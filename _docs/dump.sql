-- trigger定义。
CREATE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'UPDATE') THEN
        NEW.updated_at := now();
        return NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE TABLE "passwords"(
    "user_id" UUID NOT NULL,
    "record" SMALLINT NOT NULL,
    "hashed_password" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    PRIMARY KEY("user_id", "record")
);

CREATE TABLE "todo_jobs"(
    "user_id" UUID NOT NULL,
    "content" VARCHAR(512) NOT NULL,
    "finish" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "start" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "finished" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "status" SMALLINT NOT NULL,
    "created_at" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    PRIMARY KEY("user_id")
);

CREATE TABLE "users"(
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "email" VARCHAR(255) NOT NULL,
    "last_name" VARCHAR(48) NOT NULL,
    "first_name" VARCHAR(48) NOT NULL,
    "status" SMALLINT NOT NULL,
    "created_at" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    PRIMARY KEY("id")
);

CREATE TABLE "job_status_master"(
    "code" SMALLINT NOT NULL,
    "mark" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    PRIMARY KEY("code")
);

CREATE TABLE "user_status_master"(
    "code" SMALLINT NOT NULL,
    "mark" VARCHAR(255) NOT NULL,
    "created_at" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    "updated_at" TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    PRIMARY KEY("code")
);

ALTER TABLE "todo_jobs" ADD CONSTRAINT "todo_jobs_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "users"("id");
ALTER TABLE "passwords" ADD CONSTRAINT "passwords_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "users"("id");
ALTER TABLE "users" ADD CONSTRAINT "users_status_foreign" FOREIGN KEY("status") REFERENCES "user_status_master"("code");
ALTER TABLE "todo_jobs" ADD CONSTRAINT "todo_jobs_status_foreign" FOREIGN KEY("status") REFERENCES "job_status_master"("code");

-- trigger添加。
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
CREATE TRIGGER trg_passwords_updated_at BEFORE UPDATE ON passwords FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
CREATE TRIGGER trg_todo_jobs_updated_at BEFORE UPDATE ON todo_jobs FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
CREATE TRIGGER trg_job_status_master_updated_at BEFORE UPDATE ON job_status_master FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
CREATE TRIGGER trg_user_status_master_updated_at BEFORE UPDATE ON user_status_master FOR EACH ROW EXECUTE PROCEDURE set_updated_at();

-- master data
INSERT INTO job_status_master (code, mark) VALUES (1, '处理中');
INSERT INTO job_status_master (code, mark) VALUES (2, '已过时');
INSERT INTO job_status_master (code, mark) VALUES (3, '已完成');
INSERT INTO job_status_master (code, mark) VALUES (9, '已删除');

INSERT INTO user_status_master (code, mark) VALUES (1, '未认证');
INSERT INTO user_status_master (code, mark) VALUES (2, '未完善');
INSERT INTO user_status_master (code, mark) VALUES (9, '停用');