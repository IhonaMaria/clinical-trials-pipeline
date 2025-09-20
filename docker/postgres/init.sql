-- Create medallion architecture schemas
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Give ownership to default user
ALTER SCHEMA bronze OWNER TO user;
ALTER SCHEMA silver OWNER TO user;
ALTER SCHEMA gold OWNER TO user;
