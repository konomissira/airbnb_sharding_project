CREATE TABLE IF NOT EXISTS listings (
    id BIGINT PRIMARY KEY,
    name TEXT,
    host_id BIGINT,
    host_name TEXT,
    neighbourhood TEXT,
    latitude FLOAT,
    longitude FLOAT,
    room_type TEXT,
    price FLOAT,
    minimum_nights INT,
    number_of_reviews INT,
    last_review DATE,
    reviews_per_month FLOAT,
    calculated_host_listings_count INT,
    availability_365 INT,
    number_of_reviews_ltm INT
);
