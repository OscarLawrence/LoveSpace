"""
Simple DuckDB schema for code context storage.
"""

CREATE_SCHEMA = """
-- Create sequences for auto-incrementing IDs
CREATE SEQUENCE IF NOT EXISTS seq_documentation;

-- Documentation storage
CREATE TABLE IF NOT EXISTS documentation (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_documentation'),
    entity_type VARCHAR NOT NULL,  -- 'module', 'function', 'class', 'adr', 'guide'
    entity_id VARCHAR NOT NULL,    -- reference to code element or unique identifier
    doc_type VARCHAR NOT NULL,     -- 'api', 'guide', 'adr', 'example', 'overview'
    title VARCHAR NOT NULL,
    content TEXT NOT NULL,         -- markdown content
    metadata JSON,                 -- tags, version, author, etc
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sequences for auto-incrementing IDs
CREATE SEQUENCE IF NOT EXISTS seq_functions;
CREATE SEQUENCE IF NOT EXISTS seq_classes;
CREATE SEQUENCE IF NOT EXISTS seq_patterns;
CREATE SEQUENCE IF NOT EXISTS seq_relationships;

-- Functions and methods
CREATE TABLE IF NOT EXISTS functions (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_functions'),
    name VARCHAR NOT NULL,
    language VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    line_number INTEGER,
    params JSON,
    return_type VARCHAR,
    docstring TEXT,
    body_hash VARCHAR,
    embedding FLOAT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Classes and types
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_classes'),
    name VARCHAR NOT NULL,
    language VARCHAR NOT NULL,
    file_path VARCHAR NOT NULL,
    line_number INTEGER,
    methods JSON,
    properties JSON,
    docstring TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Code patterns and usage examples
CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_patterns'),
    name VARCHAR NOT NULL,
    language VARCHAR NOT NULL,
    pattern_type VARCHAR NOT NULL, -- auth, db, api, etc
    code_snippet TEXT NOT NULL,
    usage_context TEXT,
    dependencies JSON,
    success_count INTEGER DEFAULT 0,
    embedding FLOAT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Relationships between code elements
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_relationships'),
    from_type VARCHAR NOT NULL, -- function, class, pattern
    from_id INTEGER NOT NULL,
    to_type VARCHAR NOT NULL,
    to_id INTEGER NOT NULL,
    relationship_type VARCHAR NOT NULL, -- calls, inherits, uses, implements
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- External documentation cache (stdlib, 3rd party)
CREATE SEQUENCE IF NOT EXISTS seq_external_docs;

CREATE TABLE IF NOT EXISTS external_docs (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_external_docs'),
    source VARCHAR NOT NULL,       -- 'python_stdlib', 'sphinx', 'github'
    entity_id VARCHAR NOT NULL,    -- 'ast.parse', 'requests.get'
    content TEXT NOT NULL,         -- dense format
    metadata JSON,                 -- url, version, etc
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_functions_name ON functions(name);
CREATE INDEX IF NOT EXISTS idx_functions_language ON functions(language);
CREATE INDEX IF NOT EXISTS idx_classes_name ON classes(name);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);

-- Vector similarity indexes (skip for BLOB type)
-- CREATE INDEX IF NOT EXISTS idx_functions_embedding ON functions (embedding);
-- CREATE INDEX IF NOT EXISTS idx_patterns_embedding ON patterns (embedding);
CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_type, from_id);
CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_type, to_id);
CREATE INDEX IF NOT EXISTS idx_docs_entity ON documentation(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_docs_type ON documentation(doc_type);
CREATE INDEX IF NOT EXISTS idx_external_docs_source ON external_docs(source);
CREATE INDEX IF NOT EXISTS idx_external_docs_entity ON external_docs(entity_id);

-- Memory persistence tables for Om upgrade
CREATE SEQUENCE IF NOT EXISTS seq_module_workspaces;
CREATE SEQUENCE IF NOT EXISTS seq_sessions;
CREATE SEQUENCE IF NOT EXISTS seq_preferences;
CREATE SEQUENCE IF NOT EXISTS seq_project_states;
CREATE SEQUENCE IF NOT EXISTS seq_learning_data;
CREATE SEQUENCE IF NOT EXISTS seq_decisions;
CREATE SEQUENCE IF NOT EXISTS seq_module_handoffs;

-- Module isolation workspaces
CREATE TABLE IF NOT EXISTS module_workspaces (
    id VARCHAR PRIMARY KEY,
    module_name VARCHAR NOT NULL,
    task_scope VARCHAR NOT NULL,
    isolated_files JSON,
    dependencies JSON,
    boundaries JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

-- Module boundaries and interfaces
CREATE TABLE IF NOT EXISTS module_boundaries (
    module_name VARCHAR PRIMARY KEY,
    allowed_dependencies JSON,
    interface_contracts JSON,
    isolation_rules JSON,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session management
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL,
    module_name VARCHAR,
    context_data JSON,
    isolated_workspace_id VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User preferences
CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_preferences'),
    category VARCHAR NOT NULL,
    key VARCHAR NOT NULL,
    value JSON NOT NULL,
    weight REAL DEFAULT 1.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Project states
CREATE TABLE IF NOT EXISTS project_states (
    project_id VARCHAR PRIMARY KEY,
    state_data JSON,
    architecture_decisions JSON,
    module_structure JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Learning system data
CREATE TABLE IF NOT EXISTS learning_data (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_learning_data'),
    task_type VARCHAR NOT NULL,
    module_context VARCHAR,
    input_context TEXT,
    output_result TEXT,
    user_rating INTEGER,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Decision tracking
CREATE TABLE IF NOT EXISTS decisions (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_decisions'),
    decision_type VARCHAR NOT NULL,
    module_name VARCHAR,
    context TEXT,
    choice VARCHAR NOT NULL,
    outcome TEXT,
    success_rating INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Module handoffs
CREATE TABLE IF NOT EXISTS module_handoffs (
    id INTEGER PRIMARY KEY DEFAULT nextval('seq_module_handoffs'),
    from_module VARCHAR NOT NULL,
    to_module VARCHAR NOT NULL,
    handoff_context JSON,
    interface_changes JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Memory indexes
CREATE INDEX IF NOT EXISTS idx_module_workspaces_module ON module_workspaces(module_name);
CREATE INDEX IF NOT EXISTS idx_module_workspaces_active ON module_workspaces(active);
CREATE INDEX IF NOT EXISTS idx_sessions_project ON sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_sessions_module ON sessions(module_name);
CREATE INDEX IF NOT EXISTS idx_preferences_category ON preferences(category);
CREATE INDEX IF NOT EXISTS idx_learning_data_task ON learning_data(task_type);
CREATE INDEX IF NOT EXISTS idx_learning_data_module ON learning_data(module_context);
CREATE INDEX IF NOT EXISTS idx_decisions_type ON decisions(decision_type);
CREATE INDEX IF NOT EXISTS idx_decisions_module ON decisions(module_name);
CREATE INDEX IF NOT EXISTS idx_handoffs_modules ON module_handoffs(from_module, to_module);
"""
