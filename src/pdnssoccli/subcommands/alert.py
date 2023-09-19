import click
import logging

from pdnssoccli.subcommands.utils import make_sync
from pdnssoccli.utils.emails import Email

logger = logging.getLogger("pdnssoccli")

@click.command(help="Send alert")
@click.argument(
    'files',
    nargs=-1,
    type=click.Path(
        file_okay=True,
        dir_okay=True,
        readable=True,
        allow_dash=True
    )
)
@click.option(
    'logging_level',
    '--logging',
    type=click.Choice(['INFO','WARN','DEBUG','ERROR']),
    default="INFO"
)


@make_sync
@click.pass_context
async def alert(ctx, **kwargs):

    alerts_config = ctx.obj['CONFIG']['alerts']

    # Configure logging
    logging.basicConfig(
        level=ctx.obj['CONFIG']['logging_level']
    )
        
    if "email" in alerts_config.keys():
        alerts = ["X"] # TODO: consume this information from alerts.log
        email_config = alerts_config["email"]
        email = Email(email_config)
        email.send_email(alert)
