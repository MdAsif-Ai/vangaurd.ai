"""initial foundation schema

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00

Creates all Phase 1 tables: organizations, users, documents,
document_versions, financial_facts, research_jobs, research_messages,
claims, evidence, calculations and audit_logs.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def _enum(name: str, *values: str) -> sa.Enum:
    """Portable enum type: VARCHAR(50) plus a named CHECK constraint."""
    return sa.Enum(*values, name=name, native_enum=False, length=50)


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organizations")),
        sa.UniqueConstraint("name", name=op.f("uq_organizations_name")),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role", _enum("userrole", "admin", "user"), server_default="user", nullable=False
        ),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_users_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index(op.f("ix_users_organization_id"), "users", ["organization_id"], unique=False)
    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("document_type", sa.String(length=100), nullable=True),
        sa.Column("fiscal_year", sa.Integer(), nullable=True),
        sa.Column("storage_key", sa.String(length=1024), nullable=False),
        sa.Column(
            "status",
            _enum("documentstatus", "uploaded", "processing", "ready", "failed"),
            server_default="uploaded",
            nullable=False,
        ),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_documents_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")),
    )
    op.create_index(
        op.f("ix_documents_organization_id"), "documents", ["organization_id"], unique=False
    )
    op.create_index(op.f("ix_documents_status"), "documents", ["status"], unique=False)
    op.create_table(
        "document_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=128), nullable=True),
        sa.Column("storage_key", sa.String(length=1024), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_document_versions_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_document_versions")),
        sa.UniqueConstraint(
            "document_id", "version", name=op.f("uq_document_versions_document_id_version")
        ),
    )
    op.create_index(
        op.f("ix_document_versions_document_id"), "document_versions", ["document_id"], unique=False
    )
    op.create_table(
        "financial_facts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("metric", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Numeric(precision=24, scale=6), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=True),
        sa.Column("period", sa.String(length=50), nullable=True),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_financial_facts_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_financial_facts")),
    )
    op.create_index(
        op.f("ix_financial_facts_document_id"), "financial_facts", ["document_id"], unique=False
    )
    op.create_table(
        "research_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column(
            "status",
            _enum("researchstatus", "queued", "running", "completed", "failed", "aborted"),
            server_default="queued",
            nullable=False,
        ),
        sa.Column(
            "mode", _enum("researchmode", "fast", "deep"), server_default="fast", nullable=False
        ),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_research_jobs_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_research_jobs_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_research_jobs")),
    )
    op.create_index(
        op.f("ix_research_jobs_organization_id"), "research_jobs", ["organization_id"], unique=False
    )
    op.create_index(op.f("ix_research_jobs_user_id"), "research_jobs", ["user_id"], unique=False)
    op.create_index(op.f("ix_research_jobs_status"), "research_jobs", ["status"], unique=False)
    op.create_table(
        "research_messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("research_job_id", sa.Uuid(), nullable=False),
        sa.Column(
            "role", _enum("messagerole", "user", "assistant", "system", "tool"), nullable=False
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["research_job_id"],
            ["research_jobs.id"],
            name=op.f("fk_research_messages_research_job_id_research_jobs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_research_messages")),
    )
    op.create_index(
        op.f("ix_research_messages_research_job_id"),
        "research_messages",
        ["research_job_id"],
        unique=False,
    )
    op.create_table(
        "claims",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("research_job_id", sa.Uuid(), nullable=False),
        sa.Column("claim", sa.Text(), nullable=False),
        sa.Column("claim_type", sa.String(length=100), nullable=True),
        sa.Column(
            "status",
            _enum("claimstatus", "pending", "supported", "contradicted", "insufficient_evidence"),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["research_job_id"],
            ["research_jobs.id"],
            name=op.f("fk_claims_research_job_id_research_jobs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_claims")),
    )
    op.create_index(op.f("ix_claims_research_job_id"), "claims", ["research_job_id"], unique=False)
    op.create_table(
        "evidence",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("claim_id", sa.Uuid(), nullable=False),
        sa.Column("document_id", sa.Uuid(), nullable=True),
        sa.Column("chunk_id", sa.String(length=255), nullable=True),
        sa.Column(
            "source_type",
            _enum("sourcetype", "internal_document", "web", "financial_data"),
            nullable=False,
        ),
        sa.Column("page", sa.Integer(), nullable=True),
        sa.Column("passage", sa.Text(), nullable=False),
        sa.Column(
            "support_status",
            _enum("supportstatus", "pending", "supports", "contradicts", "insufficient_evidence"),
            server_default="pending",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["claim_id"],
            ["claims.id"],
            name=op.f("fk_evidence_claim_id_claims"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            name=op.f("fk_evidence_document_id_documents"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_evidence")),
    )
    op.create_index(op.f("ix_evidence_claim_id"), "evidence", ["claim_id"], unique=False)
    op.create_index(op.f("ix_evidence_document_id"), "evidence", ["document_id"], unique=False)
    op.create_table(
        "calculations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("claim_id", sa.Uuid(), nullable=False),
        sa.Column("operation", sa.String(length=100), nullable=False),
        sa.Column("inputs", sa.JSON(), nullable=True),
        sa.Column("formula", sa.Text(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["claim_id"],
            ["claims.id"],
            name=op.f("fk_calculations_claim_id_claims"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_calculations")),
    )
    op.create_index(op.f("ix_calculations_claim_id"), "calculations", ["claim_id"], unique=False)
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=True),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=True),
        sa.Column("resource_id", sa.String(length=64), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index(
        op.f("ix_audit_logs_organization_id"), "audit_logs", ["organization_id"], unique=False
    )
    op.create_index(op.f("ix_audit_logs_user_id"), "audit_logs", ["user_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("calculations")
    op.drop_table("evidence")
    op.drop_table("claims")
    op.drop_table("research_messages")
    op.drop_table("research_jobs")
    op.drop_table("financial_facts")
    op.drop_table("document_versions")
    op.drop_table("documents")
    op.drop_table("users")
    op.drop_table("organizations")
