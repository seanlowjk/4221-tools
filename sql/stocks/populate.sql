CREATE or REPLACE FUNCTION random_string(length INTEGER) RETURNS TEXT AS 
$$
DECLARE
  chars TEXT[] := '{A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z}';
  result TEXT := '';
  i INTEGER := 0;
BEGIN
  IF length < 0 then
    RAISE EXCEPTION 'Given length cannot be less than 0';
  END IF;
  FOR i IN 1..length 
  LOOP
    result := result || chars[1+random()*(array_length(chars, 1)-1)];
  END LOOP;
  RETURN result;
END;
$$ LANGUAGE plpgsql;

DROP TABLE Stocks;

CREATE TABLE Stocks (
    s_id INTEGER PRIMARY KEY,
    s_qty INTEGER NOT NULL
);

INSERT INTO stocks
SELECT
  g AS s_id,
  g AS s_qty
FROM
  generate_series(0, 9999) g;

