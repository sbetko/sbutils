from bs4 import BeautifulSoup, NavigableString, Tag


def flatten_single_column_tables(soup) -> BeautifulSoup:
    """Flatten non-nested single-column tables.

    Args:
        soup (BeautifulSoup): The input HTML as a BeautifulSoup object.

    Returns:
        BeautifulSoup: The transformed HTML with specific tables flattened.
    """

    # Find all table elements
    all_tables = soup.find_all("table")

    for table in all_tables:
        # Check if the table is nested within another table
        if table.find_parent("table"):
            continue  # Skip nested tables

        # Find all direct tr children of the table
        rows = table.find_all("tr", recursive=False)

        # Verify that all rows have exactly one td or th
        single_column = True
        for row in rows:
            # Consider both <td> and <th> for flexibility
            cells = row.find_all(["td", "th"], recursive=False)
            if len(cells) != 1:
                single_column = False
                break  # No need to check further if any row has multiple cells

        if not single_column:
            continue  # Skip tables that do not have exactly one column

        # List to hold the new content that will replace the table
        new_contents = []

        for row in rows:
            cell = row.find(["td", "th"], recursive=False)
            if cell:
                # Iterate over the contents of the cell
                for content in cell.contents:
                    # If the content is a NavigableString or a Tag, append it
                    if isinstance(content, (NavigableString, Tag)):
                        new_contents.append(content)
            # After each row's content, append a <br/> tag for separation
            new_contents.append(soup.new_tag("br"))

        # Insert the new contents before the table in the DOM
        for content in new_contents:
            table.insert_before(content)

        # Remove the original table from the DOM
        table.decompose()

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
