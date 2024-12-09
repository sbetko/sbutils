from bs4 import BeautifulSoup


def flatten_single_column_tables(soup):
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if all(len(row.find_all(["td", "th"])) == 1 for row in rows):
            items = [
                cell.get_text(strip=True)
                for row in rows
                for cell in row.find_all(["td", "th"])
            ]
            table.replace_with("\n".join(f"- {item}" for item in items))
    return soup


def promote_top_row_headers(soup):
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        if rows and len(rows[0].find_all(["td", "th"], colspan=True)) == len(
            rows[0].find_all(["td", "th"])
        ):
            header = rows[0].get_text(strip=True)
            rows[0].decompose()
            table.insert_before(f"## {header}\n")
    return soup


def unnest_nested_tables(soup):
    for table in soup.find_all("table"):
        nested_tables = table.find_all("table")
        for nested_table in nested_tables:
            table.insert_before(nested_table.extract())
    return soup


def rebuild_tables_with_span_attributes(soup):
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["td", "th"])
            for cell in cells:
                rowspan = int(cell.get("rowspan", 1))
                colspan = int(cell.get("colspan", 1))

                # Handle `rowspan`
                if rowspan > 1:
                    next_rows = rows[rows.index(row) + 1 : rows.index(row) + rowspan]
                    for r in next_rows:
                        new_cell = soup.new_tag(cell.name)
                        new_cell.string = cell.get_text(strip=True)
                        r.insert(len(r.find_all(["td", "th"])), new_cell)
                    cell.attrs.pop("rowspan", None)

                # Handle `colspan`
                if colspan > 1:
                    for _ in range(colspan - 1):
                        new_cell = soup.new_tag(cell.name)
                        new_cell.string = cell.get_text(strip=True)
                        row.insert(row.find_all(["td", "th"]).index(cell) + 1, new_cell)
                    cell.attrs.pop("colspan", None)
    return soup


def combine_adjacent_empty_rows(soup):
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for i in range(len(rows) - 1):
            if not rows[i].get_text(strip=True) and not rows[i + 1].get_text(
                strip=True
            ):
                rows[i].decompose()
    return soup


def add_table_captions(soup):
    for table in soup.find_all("table"):
        caption = table.find("caption")
        if caption:
            table.insert_before(f"**{caption.get_text(strip=True)}**\n")
            caption.decompose()
    return soup


def parse_html_to_markdown_friendly_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Apply transformations in order
    soup = flatten_single_column_tables(soup)
    soup = promote_top_row_headers(soup)
    soup = unnest_nested_tables(soup)
    soup = rebuild_tables_with_span_attributes(soup)
    soup = combine_adjacent_empty_rows(soup)
    soup = add_table_captions(soup)

    return str(soup)


# Example Usage
def main():
    # Example HTML input
    html = """
    <table>
        <tr><td colspan="2">Header spanning two columns</td></tr>
        <tr><td>Row 1, Col 1</td><td>Row 1, Col 2</td></tr>
        <tr><td>Row 2, Col 1</td><td>Row 2, Col 2</td></tr>
        <tr><td><table><tr><td>Nested Row 1</td></tr></table></td></tr>
    </table>
    """
    transformed_html = parse_html_to_markdown_friendly_html(html)
    print(transformed_html)

    html = """
    <table>
        <tr><td colspan="2">Header spanning two columns</td><td> Header 3</td></tr>
        <tr><td>Row 1, Col 1</td><td>Row 1, Col 2</td><td>Row 1, Col 3</td></tr>
        <tr><td>Row 2, Col 1</td><td>Row 2, Col 2</td><td>Row 2, Col 3</td></tr>
        <tr><td><table><tr><td>Nested Row 1</td></tr></table></td></tr>
    </table>
    """
    transformed_html = parse_html_to_markdown_friendly_html(html)
    print(transformed_html)


if __name__ == "__main__":
    main()
