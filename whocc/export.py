from .schemas import AtcL1234Format, AtcL5Format


def csv_store(filename: str, fieldnames: list[str], data: list[AtcL1234Format | AtcL5Format] | None) -> None:
    import csv
    import pathlib
    if data is not None:
        with open(pathlib.Path("export_csv") / f"{filename}.csv", "w") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            for item in data:
                writer.writerow(item.model_dump(exclude_defaults=True, by_alias=True))
