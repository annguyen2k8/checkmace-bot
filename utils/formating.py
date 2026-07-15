def bold(text:str) -> str:
    return "**{}**".format(text)

def box(text:str, lang="") -> str:
    return "```{}\n{}\n```".format(lang, text)

def inline(text:str) -> str:
    return "`{}`".format(text)

def italics(text:str) -> str:
    return "*{}*".format(text)

def strikethrough(text:str) -> str:
    return "~~{}~~".format(text)

def underline(text:str) -> str:
    return "__{}__".format(text)

def escape(text, *, mass_mentions=False, formatting=False) -> str:
    if mass_mentions:
        text = text.replace("@everyone", "@\u200beveryone")
        text = text.replace("@here", "@\u200bhere")
    if formatting:
        text = (text.replace("`", "\\`")
                    .replace("*", "\\*")
                    .replace("_", "\\_")
                    .replace("~", "\\~"))
    return text

def escape_mass_mentions(text:str) -> str:
    return escape(text, mass_mentions=True)

def time(timestamp:float) -> str:
    return "<t:{:1.0f}>".format(timestamp)

def format_time(uptime:float) -> str:
    days, remainder = divmod(uptime, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"**`{int(days)}d` `{int(hours)}h` `{int(minutes)}m` `{int(seconds)}s`**"