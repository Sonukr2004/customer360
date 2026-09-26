from .pipeline import extract_all


def main():
    data = extract_all()

    for source, result in data.items():
        print(
            f"{source}: "
            f"{len(result['data'])} records extracted"
        )


if __name__ == "__main__":
    main()