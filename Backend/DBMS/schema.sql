
-- FloodSense: Database Schema
-- Run this file against the floodsense_db database.

CREATE TABLE IF NOT EXISTS relief_requests (
    request_id VARCHAR(50) PRIMARY KEY,
    location TEXT NOT NULL,
    need TEXT NOT NULL,
    urgency_score NUMERIC(4,2) NOT NULL
        CHECK (urgency_score >= 0 AND urgency_score <= 10),
    people_affected INTEGER NOT NULL
        CHECK (people_affected >= 0),
    arrival_time INTEGER NOT NULL
        CHECK (arrival_time >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'allocated', 'completed')),
    source_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resource_inventory (
    resource_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    resource_name TEXT NOT NULL UNIQUE,
    available_quantity INTEGER NOT NULL DEFAULT 0
        CHECK (available_quantity >= 0),
    unit TEXT NOT NULL,
    warehouse_location TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS resource_allocations (
    allocation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    request_id VARCHAR(50) NOT NULL
        REFERENCES relief_requests(request_id),
    resource_id BIGINT NOT NULL
        REFERENCES resource_inventory(resource_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    allocated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for commonly used searches
CREATE INDEX IF NOT EXISTS idx_relief_requests_status
    ON relief_requests(status);

CREATE INDEX IF NOT EXISTS idx_relief_requests_location
    ON relief_requests(location);

CREATE INDEX IF NOT EXISTS idx_relief_requests_urgency
    ON relief_requests(urgency_score DESC);

CREATE INDEX IF NOT EXISTS idx_allocations_request
    ON resource_allocations(request_id);

-- Summary view for requests and their allocations
CREATE OR REPLACE VIEW relief_allocation_summary AS
SELECT
    rr.request_id,
    rr.location,
    rr.need,
    rr.urgency_score,
    rr.status,
    ri.resource_name,
    ra.quantity,
    ra.allocated_at
FROM relief_requests AS rr
LEFT JOIN resource_allocations AS ra
    ON rr.request_id = ra.request_id
LEFT JOIN resource_inventory AS ri
    ON ra.resource_id = ri.resource_id;