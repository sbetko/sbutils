from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
from bs4 import BeautifulSoup
import random
from rich import print


@dataclass
class TextContent:
    """Base class for text content elements"""

    text: str

    def to_html(self) -> str:
        raise NotImplementedError


@dataclass
class Header(TextContent):
    """Represents an HTML header element"""

    level: int = 1

    def to_html(self) -> str:
        return f"<h{self.level}>{self.text}</h{self.level}>"


@dataclass
class Paragraph(TextContent):
    """Represents an HTML paragraph element"""

    def to_html(self) -> str:
        return f"<p>{self.text}</p>"


@dataclass
class TableCell:
    """Represents a single cell in a table"""

    content: List[Union[TextContent, "Table"]]

    def to_html(self) -> str:
        return "".join(element.to_html() for element in self.content)


@dataclass
class Table:
    """Represents an HTML table with potentially nested content"""

    rows: int
    cols: int
    default_content: List[Union[TextContent, "Table"]]
    cell_overrides: Dict[Tuple[int, int], List[Union[TextContent, "Table"]]] = None

    def __post_init__(self):
        if self.cell_overrides is None:
            self.cell_overrides = {}

    def get_cell_content(self, row: int, col: int) -> List[Union[TextContent, "Table"]]:
        """Get content for a specific cell, using override if available"""
        return self.cell_overrides.get((row, col), self.default_content)

    def to_html(self) -> str:
        rows_html = []
        for r in range(self.rows):
            cells = []
            for c in range(self.cols):
                content = self.get_cell_content(r, c)
                cell = TableCell(content)
                cells.append(f"<td>{cell.to_html()}</td>")
            rows_html.append(f"<tr>{''.join(cells)}</tr>")
        return f"<table border='1' cellspacing='0' cellpadding='5'>{''.join(rows_html)}</table>"


class DocumentGenerator:
    """Handles generation of HTML documents from specifications"""

    def __init__(self):
        self._words = (
            "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor "
            "incididunt ut labore et dolore magna aliqua"
        ).split()

    def generate_text(self, length: int) -> str:
        """Generate lorem ipsum text of approximately specified length"""
        result = []
        current_length = 0

        while current_length < length:
            word = random.choice(self._words)
            if current_length + len(word) + 1 <= length:
                result.append(word)
                current_length += len(word) + 1
            else:
                remaining = length - current_length
                result.append(word[:remaining])
                break

        return " ".join(result)

    def create_element(self, spec: Dict) -> Union[TextContent, Table]:
        """Create a document element from a specification"""
        if spec["type"] == "paragraph":
            return Paragraph(self.generate_text(spec.get("length", 100)))
        elif spec["type"] == "header":
            return Header(spec.get("text", "Header"), spec.get("level", 1))
        elif spec["type"] == "table":
            table_spec = spec["table"]
            return Table(
                rows=table_spec["rows"],
                cols=table_spec["cols"],
                default_content=[
                    self.create_element(c) for c in table_spec["cell_fill"]
                ],
                cell_overrides={
                    pos: [self.create_element(c) for c in content]
                    for pos, content in table_spec.get("cell_overrides", {}).items()
                },
            )
        raise ValueError(f"Unknown element type: {spec['type']}")

    def generate_document(self, layout_spec: List[Dict]) -> str:
        """Generate a complete HTML document from a layout specification"""
        elements = [self.create_element(spec) for spec in layout_spec]
        body = "".join(element.to_html() for element in elements)
        return f"<html><body>{body}</body></html>"


class DocumentParser:
    """Handles parsing of HTML documents back into specifications"""

    def _parse_element(self, element) -> Optional[Dict]:
        """Parse a single HTML element into a specification"""
        if isinstance(element, str) and element.strip():
            return {"type": "paragraph"}

        if not hasattr(element, "name"):
            return None

        if element.name == "p":
            return {"type": "paragraph"}
        elif element.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            return {"type": "header"}
        elif element.name == "table":
            return {"type": "table", "table": self._parse_table(element)}
        return None

    def _parse_table(self, table_element) -> Dict:
        """Parse an HTML table element into a table specification"""
        rows = table_element.find_all("tr", recursive=False)
        row_count = len(rows)
        col_count = max(
            (len(row.find_all(["td", "th"], recursive=False)) for row in rows),
            default=0,
        )

        cell_overrides = {}
        for r_idx, row in enumerate(rows):
            for c_idx, cell in enumerate(row.find_all(["td", "th"], recursive=False)):
                content = []
                for child in cell.children:
                    if spec := self._parse_element(child):
                        content.append(spec)
                if content:
                    cell_overrides[(r_idx, c_idx)] = content

        return {
            "rows": row_count,
            "cols": col_count,
            "cell_fill": [{"type": "paragraph"}],
            "cell_overrides": cell_overrides,
        }

    def parse_document(self, html_content: str) -> List[Dict]:
        """Parse an HTML document into a layout specification"""
        soup = BeautifulSoup(html_content, "html.parser")
        if not soup.body:
            return []

        spec = []
        for element in soup.body.children:
            if parsed := self._parse_element(element):
                spec.append(parsed)
        return spec


def test_system():
    """Test the document generation and parsing system"""
    # Test specification similar to the one in the example
    layout_spec = [
        {"type": "paragraph", "length": 500},
        {"type": "header", "level": 1, "text": "Table 1. Example Table"},
        {
            "type": "table",
            "table": {
                "rows": 3,
                "cols": 2,
                "cell_fill": [{"type": "paragraph", "length": 100}],
                "cell_overrides": {
                    (0, 0): [{"type": "header", "text": "Section"}],
                    (0, 1): [{"type": "header", "text": "Content"}],
                    (1, 1): [
                        {"type": "paragraph", "length": 200},
                        {
                            "type": "table",
                            "table": {
                                "rows": 2,
                                "cols": 2,
                                "cell_fill": [{"type": "paragraph", "length": 50}],
                                "cell_overrides": {
                                    (0, 1): [{"type": "paragraph", "length": 10}],
                                },
                            },
                        },
                    ],
                },
            },
        },
        {"type": "paragraph", "length": 300},
    ]

    # Generate and parse the document
    generator = DocumentGenerator()
    parser = DocumentParser()

    html = generator.generate_document(layout_spec)
    parsed_spec = parser.parse_document(html)

    print("Generated HTML:")
    print(html)
    print("\nParsed Specification:")
    print(parsed_spec)


if __name__ == "__main__":
    test_system()
