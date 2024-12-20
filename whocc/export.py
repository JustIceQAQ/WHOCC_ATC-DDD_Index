from .schemas import AtcL1234Format, AtcL5Format
import pathlib


def csv_store(
    filename: str,
    fieldnames: list[str],
    data: list[AtcL1234Format | AtcL5Format] | None,
) -> None:
    import csv

    if data is not None:
        folder = pathlib.Path("export_csv")
        if not folder.exists():
            folder.mkdir(exist_ok=True)
        with open(pathlib.Path("export_csv") / f"{filename}.csv", "w") as fp:
            writer = csv.DictWriter(fp, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            for item in data:
                writer.writerow(item.model_dump(exclude_defaults=True, by_alias=True))


def xlsx_store(
    filename: str,
    fieldnames: list[str],
    data: list[AtcL1234Format | AtcL5Format] | None,
):
    from openpyxl import Workbook

    if data is not None:
        folder = pathlib.Path("export_xlsx")
        if not folder.exists():
            folder.mkdir(exist_ok=True)

        wb = Workbook()
        ws = wb.active
        ws.title = f"WHOCCAtcDddIndex_{filename}"
        ws.append(fieldnames)
        for item in data:
            ws.append(
                list(item.model_dump(exclude_defaults=True, by_alias=True).values())
            )
        wb.save(folder / f"{filename}.xlsx")
