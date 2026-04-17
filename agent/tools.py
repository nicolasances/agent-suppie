from typing import List
from langchain_core.tools import tool


@tool
def get_common_items() -> List[str]:
    """Returns the list of items that are the most commonly used in the shopping list (supermarket list)"""
    return ["Bacon", "Bacon i tern", "Spaghetti", "Greek Yogurt", "Riskiks", "Majskiks", "Medister", "Pasta", "Bread", "Bread C", "Bread N"]


@tool
def add_item_to_list(item: str):
    """Adds a given item to the supermarket list (shopping list)"""
    print(f"Item {item} added to your shopping list")
