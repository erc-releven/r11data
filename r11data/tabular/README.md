# Releven Spreadsheet Conversion

The module contains triple generation logic for converting Releven spreadsheet data to STAR Graph RDF.

## URI Minting

The triple generators implemented here generally use UUID4 for unique URI generation and SHA256 hashing for reproducible URIs according to a common hash value.

See [DataModelSchemas PR #21](https://github.com/erc-releven/DataModelSchemas/pull/21) or the respective [DataModelSchemas branch](https://github.com/erc-releven/DataModelSchemas/tree/lupl/uri-policy-readme).


## Command Line Interface

The module features a simple CLI for running the triple generators and serializing RDF to files on disc.

```shell
uv run python cli.py --help
```

The above command displays a help page including all currently defined triple generators.

To run all defined triple generators, simply execute the CLI without arguments, optionally with an `--output` option:

```shell
uv run python cli.py --output somewhere/
```

The default output location is `output/` relativ to the shell the script is run in.

To run only a selection of triple generators, pass the triple generator names as arguments:

```shell
uv run python cli.py persons places social_relationships
```
