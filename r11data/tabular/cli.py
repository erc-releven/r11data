from pathlib import Path

from r11data.tabular.generators import (
    actor_groups_triples,
    author_groups_triples,
    authority_status_triples,
    birth_death_triples,
    boulloteria_triples,
    correspondence_triples,
    death_triples,
    lead_seals_triples,
    location_triples,
    manuscripts_triples,
    persons_triples,
    places_triples,
    social_relationships_triples,
    text_publications_triples,
)
import typer


app = typer.Typer()


GENERATORS = {
    "actor_groups": actor_groups_triples,
    "author_groups": author_groups_triples,
    "authority_status": authority_status_triples,
    "birth_death": birth_death_triples,
    "boulloteria": boulloteria_triples,
    "correspondence": correspondence_triples,
    "lead_seals": lead_seals_triples,
    "manuscripts": manuscripts_triples,
    "persons": persons_triples,
    "places": places_triples,
    "social_relationships": social_relationships_triples,
    "text_publications": text_publications_triples,
    "deaths": death_triples,
    "locations": location_triples,
}


@app.command()
def cli(
    generators: list[str] | None = typer.Argument(
        None, help=f"Triple generators: {', '.join(GENERATORS.keys())}"
    ),
    output: Path = typer.Option(
        Path("./output"),
        "--output",
        "-o",
        help="Output directory",
        file_okay=False,
        dir_okay=True,
        writable=True,
    ),
):
    """Run selected generators and write output to a directory."""
    output.mkdir(parents=True, exist_ok=True)
    applicable_generators = GENERATORS.keys() if generators is None else generators

    for name in applicable_generators:
        if name not in GENERATORS:
            typer.echo(f"Unknown generator: {name}")
            raise typer.Exit(code=1)

        typer.echo(f"Running generator: {name}")

        output_file_path = output / f"{name}.ttl"
        generator = GENERATORS[name]

        with open(output_file_path, "w") as f:
            f.write(generator.to_graph().serialize(format="ttl"))

    typer.echo(f"Done. Output written to: {output.resolve()}")


if __name__ == "__main__":
    app()
