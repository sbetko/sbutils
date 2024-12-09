from bs4 import BeautifulSoup


def flatten_single_column_tables(soup) -> BeautifulSoup:
    """Flatten non-nested single-column tables.

    Args:
        soup (BeautifulSoup): The input HTML as a BeautifulSoup object.

    Returns:
        BeautifulSoup: The transformed HTML with specific tables flattened.
    """

    def get_table_rows(table):
        # Prefer rows from thead, tbody, tfoot if present
        sections = []
        for tag_name in ["thead", "tbody", "tfoot"]:
            section = table.find(tag_name, recursive=False)
            if section:
                sections.append(section)

        rows = []
        if sections:
            # Gather rows from these sections
            for sec in sections:
                rows.extend(sec.find_all("tr", recursive=False))
        else:
            # No thead/tbody/tfoot found; directly extract top-level rows
            rows = table.find_all("tr", recursive=False)
        return rows

    def is_top_level_table(tbl):
        return not tbl.find_parent("table")

    def is_single_column_table(tbl):
        rows = get_table_rows(tbl)
        for r in rows:
            tds = r.find_all("td", recursive=False)
            if len(tds) != 1:
                return False
        return True

    def flatten_table(tbl):
        rows = get_table_rows(tbl)
        new_contents = []

        for row in rows:
            tds = row.find_all("td", recursive=False)
            td = tds[0]
            # Extract all child nodes within the td
            for child in td.contents:
                new_contents.append(child)
            # Add a <br/> after each row
            new_contents.append(soup.new_tag("br"))

        return new_contents

    candidate_tables = [
        t
        for t in soup.find_all("table")
        if is_top_level_table(t) and is_single_column_table(t)
    ]

    for tbl in candidate_tables:
        flattened = flatten_table(tbl)
        tbl.insert_before(*flattened)
        tbl.decompose()

    return soup


def parse_html_to_markdown_friendly_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    soup = flatten_single_column_tables(soup)

    return str(soup)


def main():
    html = """
    <html>
        <body>
            <table>
                <tr><td>Header 1</td></tr>
                <tr><td>Row 1, Col 1</td></tr>
                <tr><td>Row 2, Col 1</td></tr>
                <tr><td><table><tr><td>Nested Row 1</td></tr></table></td></tr>
            </table>
        </body>
    </html>
    """

    print("Input HTML:\n", html)
    transformed_html = parse_html_to_markdown_friendly_html(html)
    print("\nTransformed HTML:\n", transformed_html)


if __name__ == "__main__":
    main()
