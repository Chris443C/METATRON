#!/usr/bin/env python3
"""METATRON - db_migrate.py  Safe, idempotent DB schema migration."""
import mysql.connector
from datetime import datetime

DB_CONFIG = {"host": "localhost", "user": "metatron", "password": "123", "database": "metatron"}

MIGRATIONS = [
    {
        "version": 1,
        "description": "Add engagements, scope_items, evidence tables",
        "statements": [
            """CREATE TABLE IF NOT EXISTS engagements (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                client_name     VARCHAR(255) NOT NULL,
                engagement_name VARCHAR(255) NOT NULL,
                test_type       ENUM('black','grey','white') NOT NULL DEFAULT 'black',
                start_date      DATE,
                end_date        DATE,
                testing_window  VARCHAR(500),
                status          ENUM('planning','active','reporting','complete') NOT NULL DEFAULT 'planning',
                created_at      DATETIME NOT NULL,
                notes           TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS scope_items (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                engagement_id   INT NOT NULL,
                item_type       ENUM('in_scope','out_of_scope') NOT NULL DEFAULT 'in_scope',
                target          VARCHAR(500) NOT NULL,
                description     VARCHAR(1000),
                FOREIGN KEY (engagement_id) REFERENCES engagements(id) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS evidence (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                sl_no           INT NOT NULL,
                engagement_id   INT,
                phase           VARCHAR(50),
                evidence_type   ENUM('screenshot','command_output','note','file_path') NOT NULL,
                label           VARCHAR(255),
                content         LONGTEXT,
                captured_at     DATETIME NOT NULL,
                FOREIGN KEY (sl_no) REFERENCES history(sl_no) ON DELETE CASCADE
            )""",
        ]
    },
    {
        "version": 2,
        "description": "Add post_exploitation, attack_paths, retest_sessions tables",
        "statements": [
            """CREATE TABLE IF NOT EXISTS post_exploitation (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                sl_no           INT NOT NULL,
                engagement_id   INT,
                technique       VARCHAR(500) NOT NULL,
                technique_type  ENUM('privesc','lateral_movement','persistence','data_access','other') NOT NULL,
                from_host       VARCHAR(255),
                to_host         VARCHAR(255),
                from_user       VARCHAR(255),
                to_user         VARCHAR(255),
                success         BOOLEAN NOT NULL DEFAULT FALSE,
                evidence_notes  TEXT,
                captured_at     DATETIME NOT NULL,
                FOREIGN KEY (sl_no) REFERENCES history(sl_no) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS attack_paths (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                sl_no           INT NOT NULL,
                engagement_id   INT,
                path_name       VARCHAR(500) NOT NULL,
                steps           TEXT NOT NULL,
                severity        ENUM('critical','high','medium','low') NOT NULL DEFAULT 'high',
                cvss_score      DECIMAL(4,1),
                ai_narrative    TEXT,
                created_at      DATETIME NOT NULL,
                FOREIGN KEY (sl_no) REFERENCES history(sl_no) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS retest_sessions (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                original_sl_no  INT NOT NULL,
                retest_sl_no    INT NOT NULL,
                engagement_id   INT,
                retested_at     DATETIME NOT NULL,
                overall_result  ENUM('all_fixed','partial','none_fixed','new_found') NOT NULL,
                notes           TEXT,
                FOREIGN KEY (original_sl_no) REFERENCES history(sl_no),
                FOREIGN KEY (retest_sl_no)   REFERENCES history(sl_no)
            )""",
        ]
    },
    {
        "version": 3,
        "description": "Extend history table with engagement_id and phase columns",
        "statements": [
            # Checked idempotently via information_schema before running
            "ALTER TABLE history ADD COLUMN engagement_id INT NULL",
            "ALTER TABLE history ADD COLUMN phase VARCHAR(50) NULL DEFAULT 'recon'",
        ]
    },
    {
        "version": 4,
        "description": "Add cloud_findings table",
        "statements": [
            """CREATE TABLE IF NOT EXISTS cloud_findings (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                sl_no           INT NOT NULL,
                engagement_id   INT,
                provider        ENUM('aws','azure','gcp','other') NOT NULL,
                service         VARCHAR(255) NOT NULL,
                finding_title   VARCHAR(500) NOT NULL,
                severity        ENUM('critical','high','medium','low','info') NOT NULL DEFAULT 'medium',
                resource_id     VARCHAR(1000),
                region          VARCHAR(100),
                description     TEXT,
                recommendation  TEXT,
                raw_output      LONGTEXT,
                tool_used       VARCHAR(100),
                captured_at     DATETIME NOT NULL,
                FOREIGN KEY (sl_no) REFERENCES history(sl_no) ON DELETE CASCADE
            )"""
        ]
    },
    {
        "version": 5,
        "description": "Add segmentation_tests table",
        "statements": [
            """CREATE TABLE IF NOT EXISTS segmentation_tests (
                id              INT AUTO_INCREMENT PRIMARY KEY,
                sl_no           INT NOT NULL,
                engagement_id   INT,
                source_host     VARCHAR(255) NOT NULL,
                dest_host       VARCHAR(255) NOT NULL,
                dest_port       INT NOT NULL,
                protocol        ENUM('tcp','udp') NOT NULL DEFAULT 'tcp',
                expected        ENUM('blocked','allowed') NOT NULL DEFAULT 'blocked',
                result          ENUM('PASS','FAIL','ERROR') NOT NULL,
                tool_used       VARCHAR(50) NOT NULL DEFAULT 'ncat',
                raw_output      TEXT,
                tester_name     VARCHAR(255),
                tested_at       DATETIME NOT NULL,
                FOREIGN KEY (sl_no) REFERENCES history(sl_no) ON DELETE CASCADE
            )"""
        ]
    },
]


def _col_exists(conn, table: str, column: str) -> bool:
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s",
        (DB_CONFIG["database"], table, column)
    )
    return cur.fetchone()[0] > 0


def create_migrations_table(conn):
    conn.cursor().execute(
        """CREATE TABLE IF NOT EXISTS schema_migrations (
            version INT PRIMARY KEY,
            description VARCHAR(500),
            applied_at DATETIME NOT NULL
        )"""
    )
    conn.commit()


def get_applied_versions(conn) -> set:
    cur = conn.cursor()
    cur.execute("SELECT version FROM schema_migrations")
    return {row[0] for row in cur.fetchall()}


def run_migrations():
    conn = mysql.connector.connect(**DB_CONFIG)
    create_migrations_table(conn)
    applied = get_applied_versions(conn)
    for m in MIGRATIONS:
        if m["version"] in applied:
            print(f"  [skip] Migration {m['version']}: {m['description']}")
            continue
        cur = conn.cursor()
        for stmt in m["statements"]:
            # Skip ALTER TABLE if column already exists (idempotency)
            if "ADD COLUMN engagement_id" in stmt and _col_exists(conn, "history", "engagement_id"):
                continue
            if "ADD COLUMN phase" in stmt and _col_exists(conn, "history", "phase"):
                continue
            cur.execute(stmt)
        cur.execute(
            "INSERT INTO schema_migrations (version, description, applied_at) VALUES (%s, %s, %s)",
            (m["version"], m["description"], datetime.now())
        )
        conn.commit()
        print(f"  [ok]   Migration {m['version']} applied: {m['description']}")
    conn.close()
    print("\nMigration complete.")


if __name__ == "__main__":
    run_migrations()
