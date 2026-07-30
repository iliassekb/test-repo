import argparse


def greet(name: str) -> str:
    return f"Hello, {name}!"


def main() -> None:
    parser = argparse.ArgumentParser(description="Print a greeting.")
    parser.add_argument("--name", default="world", help="Name to greet")
    args = parser.parse_args()
    print(greet(args.name))


if __name__ == "__main__":
    main()
