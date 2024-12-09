from bs4 import BeautifulSoup


def flatten_single_column_tables(soup) -> BeautifulSoup:
    """Flatten non-nested single-column tables.

    Args:
        soup (BeautifulSoup): The input HTML as a BeautifulSoup object.

    Returns:
        BeautifulSoup: The transformed HTML with specific tables flattened.
    """
    def is_top_level_table(tbl):
        return not tbl.find_parent("table")

    def is_single_column_table(tbl):
        rows = tbl.find_all("tr", recursive=False)
        for r in rows:
            tds = r.find_all("td", recursive=False)
            if len(tds) != 1:
                return False
        return True

    def flatten_table(tbl):
        new_contents = []
        rows = tbl.find_all("tr", recursive=False)
        for row in rows:
            tds = row.find_all("td", recursive=False)
            # Each row is guaranteed one <td> if table is single-column
            td = tds[0]
            # We want to extract the contents of the td and place them inline
            # Preserve nested tables, just unwrap the td itself
            # Extract contents but do not lose nested tags
            for child in td.contents:
                new_contents.append(child)
            # After each row, add a <br/>
            new_contents.append(soup.new_tag("br"))
        return new_contents

    # Find all candidate tables
    candidate_tables = [
        t
        for t in soup.find_all("table")
        if is_top_level_table(t) and is_single_column_table(t)
    ]

    for tbl in candidate_tables:
        flattened = flatten_table(tbl)
        # Replace the table with flattened content
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
