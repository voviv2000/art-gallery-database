TRUNCATE Artist, Customer, Exhibition, Category, Artwork, Displays, Belongs, Attends, published_images CASCADE;

-- Parent Tables
\copy Artist FROM 'data/artists.csv' WITH (FORMAT CSV, HEADER, QUOTE '"');
\copy Customer FROM 'data/customers.csv' WITH (FORMAT CSV, HEADER, QUOTE '"');
\copy Exhibition FROM 'data/exhibitions.csv' WITH (FORMAT CSV, HEADER, QUOTE '"');
\copy Category FROM 'data/categories.csv' WITH (FORMAT CSV, HEADER, QUOTE '"');

-- Artwork: This is the correct combination for quoting=1 in Pandas
\copy Artwork FROM 'data/artwork.csv' WITH (FORMAT CSV, HEADER, QUOTE '"', NULL '');

-- Relationship Tables
\copy Displays FROM 'data/displays.csv' WITH (FORMAT CSV, HEADER, QUOTE '"');
\copy Belongs FROM 'data/belongs.csv' WITH (FORMAT CSV, HEADER, QUOTE '"');
\copy Attends FROM 'data/attends.csv' WITH (FORMAT CSV, HEADER, QUOTE '"');
\copy published_images FROM 'data/published_images.csv' WITH (FORMAT CSV, HEADER, QUOTE '"');