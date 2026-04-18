from typing import List
from langchain_core.tools import tool


@tool
def add_item_to_list(item: str):
    """Adds a given item to the supermarket list (shopping list)"""
    print(f"Item {item} added to your shopping list")
