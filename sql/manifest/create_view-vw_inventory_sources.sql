CREATE OR REPLACE VIEW manifest.vw_inventory_sources AS (
	SELECT
		diid.json->>'hash' item_hash,
		diid.json->'displayProperties'->>'name' item_name,
		dcd.json->>'sourceString' item_source
	FROM manifest.mv_manifest dcd, manifest.mv_manifest diid
	WHERE dcd.table_name = 'DestinyCollectibleDefinition'
	AND diid.table_name = 'DestinyInventoryItemDefinition'
	AND dcd.json->'itemHash' = diid.json->'hash'
	ORDER BY diid.json->'displayProperties'->>'name'
);