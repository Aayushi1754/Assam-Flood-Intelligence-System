# updated
-- FloodSense: Sample data for testing
-- Safe to run multiple times without duplicating these records.

-- Insert sample flood-relief requests
INSERT INTO relief_requests
    (request_id, location, need, urgency_score,
     people_affected, arrival_time, status, source_text,
     extracted_keywords, urgency_level)
VALUES
    ('REQ001', 'Dibrugarh', 'water', 9.50, 120, 1, 'pending',
     'Urgent need for drinking water',
     ARRAY['water', 'urgent'], 'High'),

    ('REQ002', 'Silchar', 'food', 8.00, 80, 2, 'pending',
     'Food needed for affected families',
     ARRAY['food', 'families'], 'High'),

    ('REQ003', 'Barpeta', 'medical', 9.80, 45, 3, 'pending',
     'Medical assistance required urgently',
     ARRAY['medical', 'urgent'], 'Critical'),

    ('REQ004', 'Majuli', 'water', 9.20, 150, 4, 'pending',
     'Drinking water needed for many people',
     ARRAY['water', 'drinking'], 'High')
ON CONFLICT (request_id) DO NOTHING;


-- Insert sample resource inventory
INSERT INTO resource_inventory
    (resource_name, resource_category, available_quantity,
     unit, warehouse_location)
VALUES
    ('water', 'Water', 1000, 'litres', 'Dibrugarh'),
    ('food', 'Food', 500, 'packets', 'Silchar'),
    ('medical', 'Medical', 200, 'kits', 'Guwahati'),
    ('rescue_boats', 'Rescue', 10, 'boats', 'Majuli'),
    ('shelter_kits', 'Shelter', 100, 'kits', 'Barpeta')
ON CONFLICT (resource_name) DO NOTHING;