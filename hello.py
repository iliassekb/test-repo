import argparse


def greet(name: str, shout: bool = False) -> str:
    message = f"Hello, {name}!"
    return message.upper() if shout else message


def main() -> None:
    parser = argparse.ArgumentParser(description="Print a greeting.")
    parser.add_argument("--name", default="world", help="Name to greet")
    parser.add_argument("--shout", action="store_true", help="Print the greeting in caps")
    args = parser.parse_args()
    print(greet(args.name, args.shout))


if __name__ == "__main__":
    main()
