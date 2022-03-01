-- Database Stocks
CREATE INDEX qty_ind ON Stocks(s_qty);

SELECT * 
FROM Stocks s
WHERE s.s_qty >= 100;

EXPLAIN ANALYZE SELECT * 
FROM Stocks s
WHERE s.s_qty >= 100;

EXPLAIN ANALYZE SELECT * 
FROM Stocks s
WHERE s.s_qty >= 500;

CREATE OR REPLACE FUNCTION test(NUMERIC) 
RETURNS SETOF TEXT AS $$
BEGIN
RETURN QUERY EXECUTE 
'EXPLAIN SELECT * 
FROM Stocks s
WHERE s.s_qty >= ' ||$1 ;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION stat(NUMERIC) 
RETURNS SETOF NUMERIC AS $$
BEGIN
RETURN QUERY EXECUTE 
'SELECT ROUND((COUNT(*)::NUMERIC /(SELECT COUNT(*) 
                                         FROM Stocks))
                                        *100)
FROM Stocks s
WHERE s.s_qty >= ' ||$1 ;
END
$$ LANGUAGE plpgsql;


SELECT q.qty, stat(q.qty), 
regexp_replace((SELECT * 
FROM test(q.qty) LIMIT 1),'(\.*)\(.*','\1')
FROM (SELECT DISTINCT ROUND(s_qty::NUMERIC/100)*100
AS qty FROM Stocks) AS q
ORDER BY q.qty;

DELETE FROM Stocks WHERE s_qty=1000;

