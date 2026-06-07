-- Total content count
SELECT COUNT(*)
FROM Netflix;

-- Content type distribution
SELECT type,
       COUNT(*) AS total
FROM Netflix
GROUP BY type;

-- Top countries
SELECT country,
       COUNT(*) AS total
FROM Netflix
GROUP BY country
ORDER BY total DESC
LIMIT 10;

-- Rating distribution
SELECT rating,
       COUNT(*) AS total
FROM Netflix
GROUP BY rating
ORDER BY total DESC;

-- Latest releases
SELECT title,
       release_year
FROM Netflix
ORDER BY release_year DESC
LIMIT 10;