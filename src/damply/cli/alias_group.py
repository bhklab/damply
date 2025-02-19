import click 

import difflib
import typing



class DYMMixin:
    """
    Mixin class for click MultiCommand inherited classes
    to provide git-like *did-you-mean* functionality when
    a certain command is not registered.
    """

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.max_suggestions = kwargs.pop("max_suggestions", 3)
        self.cutoff = kwargs.pop("cutoff", 0.5)
        super().__init__(*args, **kwargs)  # type: ignore

    def resolve_command(
        self, ctx: click.Context, args: typing.List[str]
    ) -> typing.Tuple[
        typing.Optional[str], typing.Optional[click.Command], typing.List[str]
    ]:
        """
        Overrides clicks ``resolve_command`` method
        and appends *Did you mean ...* suggestions
        to the raised exception message.
        """
        try:
            return super(DYMMixin, self).resolve_command(ctx, args)  # type: ignore
        except click.exceptions.UsageError as error:
            error_msg = str(error)
            original_cmd_name = click.utils.make_str(args[0])
            matches = difflib.get_close_matches(
                original_cmd_name,
                self.list_commands(ctx),  # type: ignore
                self.max_suggestions,
                self.cutoff,
            )
            if matches:
                fmt_matches = "\n    ".join(matches)
                error_msg += "\n\n"
                error_msg += f"Did you mean one of these?\n    {fmt_matches}"

            raise click.exceptions.UsageError(error_msg, error.ctx)


class DYMGroup(DYMMixin, click.Group):
    """
    click Group to provide git-like
    *did-you-mean* functionality when a certain
    command is not found in the group.
    """


class DYMCommandCollection(DYMMixin, click.CommandCollection):
    """
    click CommandCollection to provide git-like
    *did-you-mean* functionality when a certain
    command is not found in the group.
    """


class AliasedGroup(DYMGroup):
    command_class = click
    max_suggestions = 3
    cutoff = 0.5

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)

        if cmd is not None:
            return cmd.name, cmd, args
        else:
            return None, None, args