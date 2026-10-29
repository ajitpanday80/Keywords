from pathlib import Path

import click

from . import pipeline, report
from .llm import ClaudeLLM
from .models import Business


@click.group()
def main():
    """Intent-based keyword research for SEO and GEO."""


@main.command()
@click.option("--business", required=True, help="What the business/site does.")
@click.option("--audience", default="", help="Who you want to reach.")
@click.option("--market", default="US, English")
@click.option("--site-strength", type=click.Choice(["new", "growing", "established"]),
              default="new", help="Calibrates difficulty estimates.")
@click.option("--intents", default=10, show_default=True)
@click.option("--seo-per-intent", default=12, show_default=True)
@click.option("--geo-per-intent", default=8, show_default=True)
@click.option("--model", default=None, help="Defaults to $KWINTENT_MODEL or claude-opus-5-5.")
@click.option("--out", type=click.Path(path_type=Path), default=Path("out"))
def research(business, audience, market, site_strength, intents,
             seo_per_intent, geo_per_intent, model, out):
    biz = Business(description=business, audience=audience, market=market,
                   site_strength=site_strength)
    result = pipeline.run(ClaudeLLM(model), biz, intents, seo_per_intent, geo_per_intent)
    report.write(result, out)
    click.echo(f"{len(result['intents'])} intents, {len(result['seo_keywords'])} keywords, "
               f"{len(result['geo_prompts'])} GEO prompts -> {out}/")
