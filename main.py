import argparse

from radar import bot, checker, music, storage


def _local_add(query: str) -> None:
    artists = storage.load_artists()
    query = " ".join(query.split())
    if any(a.get("query", "").lower() == query.lower() for a in artists):
        print(f"already tracked: {query}")
        return
    info = music.resolve_artist(query)
    artists.append(
        {
            "query": query,
            "name": (info or {}).get("name", query),
            "picture": (info or {}).get("picture", ""),
            "deezer_id": (info or {}).get("deezer_id"),
            "link": (info or {}).get("link", ""),
            "fans": (info or {}).get("fans", 0),
        }
    )
    storage.save_artists(artists)
    print(f"added: {(info or {}).get('name', query)}")


def _local_remove(query: str) -> None:
    artists = storage.load_artists()
    kept = [
        a
        for a in artists
        if a.get("query", "").lower() != query.lower()
        and (a.get("name") or "").lower() != query.lower()
    ]
    storage.save_artists(kept)
    print("removed" if len(kept) != len(artists) else "not found")


def _local_list() -> None:
    artists = storage.load_artists()
    if not artists:
        print("no artists")
        return
    for index, artist in enumerate(artists, start=1):
        print(f"{index}. {artist.get('name') or artist.get('query')}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="concert-radar")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    commands.add_parser("bot")
    add_parser = commands.add_parser("add")
    add_parser.add_argument("artist")
    remove_parser = commands.add_parser("remove")
    remove_parser.add_argument("artist")
    commands.add_parser("list")
    args = parser.parse_args()

    if args.command == "check":
        print(f"delivered: {checker.run()}")
    elif args.command == "bot":
        bot.run_bot()
    elif args.command == "add":
        _local_add(args.artist)
    elif args.command == "remove":
        _local_remove(args.artist)
    elif args.command == "list":
        _local_list()


if __name__ == "__main__":
    main()
