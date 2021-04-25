# EpiciniumBot in Python

This is a reimplementation of EpiciniumBot, a Discord bot written in Python for the game Epicinium.

Epicinium was released on October 12th, 2020 as a free game on [Steam](https://store.steampowered.com/app/1286730/Epicinium/) and [itch.io](https://abunchofhacks.itch.io/epicinium).
The [full source code](https://github.com/abunchofhacks/Epicinium) (excluding proprietary Steam integrations) is made available under the AGPL-3.0 License.

## Support

Epicinium is and will remain free software. If you wish to support Epicinium and A Bunch of Hacks, you have the option to [name-your-own-price](https://abunchofhacks.itch.io/epicinium/purchase) or [buy the game's soundtrack](https://store.steampowered.com/app/1442600/Epicinium__Extended_Soundtrack/).

## Contents

* `epicinium_bot.py` contains the entry point for the bot
* `src/` contains separate "cogs" for handling discord commands and connecting to the game server

## Dependencies

* Python 3.6 or higher
* [discord.py](https://discordpy.readthedocs.io/) 1.7.1
* [discord.py-stubs](https://pypi.org/project/discord.py-stubs/) 1.7.1
* [discord-ext-typed-commands](https://pypi.org/project/discord-ext-typed-commands/) 1.0.3
* [aiohttp](https://pypi.org/project/aiohttp/) 3.7.4.post0
* [toml](https://pypi.org/project/toml/) 0.10.2

## License

This bot was created by [A Bunch of Hacks](https://abunchofhacks.coop).
It is made available to you under the MIT License,
as specified in `LICENSE.txt`.

The software is provided "as is", without warranty of any kind, express or
implied, including but not limited to the warranties of merchantability,
fitness for a particular purpose and noninfringement. In no event shall the
authors or copyright holders be liable for any claim, damages or other
liability, whether in an action of contract, tort or otherwise, arising from,
out of or in connection with the software or the use or other dealings in the
software.

## Credits

* Daan Mulder (original implementation in PHP)
* Sander in 't Veld (reimplementation)

## Related repositories

*  [Epicinium](https://github.com/abunchofhacks/Epicinium), the full source code of the game for which this is a Discord bot
