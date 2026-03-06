# Releven Spreadsheet Conversion

The package contains triple generation logic for converting Releven spreadsheet data to STAR Graph RDF.

## URI Reconciliation

The triple generators implemented here generally use UUID4 for unique URI generation and SHA256 hashing for reproducible URIs according to a common hash value.

Legacy URIs in the Releven GraphDB store do not use URI hashing and erog need `owl:sameAs` reconciliation.
This can be achieved by denoting a common identifier, usually a common `rdfs:label` value, and running a reconciliation INSERT request.

E.g. for reconciliation of `crm:E21_Person`:

```sparql
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>

insert {
graph <https://r11.eu/rdf/resource/connections> {
	?person1 owl:sameAs ?person2 .
  }
}
where {
  ?person1 a crm:E21_Person ;
		   rdfs:label ?label .

  ?person2 a crm:E21_Person ;
		   rdfs:label ?label .

  filter (str(?person1) < str(?person2))
}
```
