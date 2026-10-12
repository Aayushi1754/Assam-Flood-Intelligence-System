#This file will insert sample flood-relief requests and inventory

-- FloodSense: Sample data for testing
-- Safe to run multiple times without duplicating these records.

INSERT INTO relief_requests
    (request_id, location, need, urgency_score,
     people_affected, arrival_time, status)
VALUES
    ('REQ001', 'Dibrugarh', 'water', 9.50, 120, 1, 'pending'),
    ('REQ002', 'Silchar',   'food',  8.00,  80, 2, 'pending'),
    ('REQ003', 'Barpeta',   'medical', 9.80, 45, 3, 'pending'),
    ('REQ004', 'Majuli',    'water',  9.20, 150, 4, 'pending')
ON CONFLICT (request_id) DO NOTHING;

INSERT INTO resource_inventory
    (resource_name, available_quantity, unit, warehouse_location)
VALUES
    ('water',   1000, 'litres',  'Dibrugarh'),
    ('food',     500, 'packets', 'Silchar'),
    ('medical',  200, 'kits',    'Guwahati')
ON CONFLICT (resource_name) DO NOTHING;