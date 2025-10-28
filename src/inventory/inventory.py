from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from .item import Item, ItemType

@dataclass
class Inventory:
    """Manages a collection of items with a limited capacity."""
    capacity: int = 20
    hotbar_size: int = 8
    items: List[Optional[Item]] = field(default_factory=list)
    selected_slot: int = 0
    
    def __post_init__(self):
        """Initialize the inventory with empty slots."""
        # Ensure the inventory has the correct number of slots
        while len(self.items) < self.capacity:
            self.items.append(None)
    
    def add_item(self, item_type: ItemType, quantity: int = 1, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add an item to the inventory.
        
        Args:
            item_type: The type of item to add
            quantity: How many of the item to add
            data: Optional data associated with the item
            
        Returns:
            bool: True if all items were added, False otherwise
        """
        if quantity <= 0:
            return False
            
        item = Item(item_type, 1, data=data)
        
        # First, try to stack with existing items of the same type
        if item.max_stack > 1:
            for i, existing_item in enumerate(self.items):
                if existing_item is not None and existing_item.can_stack_with(item):
                    # Calculate how many can be added to this stack
                    can_add = min(quantity, existing_item.max_stack - existing_item.quantity)
                    existing_item.quantity += can_add
                    quantity -= can_add
                    
                    if quantity <= 0:
                        return True
        
        # If there are still items left, add them to empty slots
        if quantity > 0:
            for i in range(self.capacity):
                if self.items[i] is None:
                    # Add as many as possible to this slot
                    add_quantity = min(quantity, item.max_stack)
                    self.items[i] = Item(item_type, add_quantity, item.max_stack, data)
                    quantity -= add_quantity
                    
                    if quantity <= 0:
                        return True
        
        # If we get here, there wasn't enough space for all items
        return quantity <= 0
    
    def remove_item(self, item_type: ItemType, quantity: int = 1) -> bool:
        """
        Remove items from the inventory.
        
        Args:
            item_type: The type of item to remove
            quantity: How many to remove
            
        Returns:
            bool: True if the items were removed, False otherwise
        """
        if quantity <= 0:
            return False
            
        # Count how many of this item we have
        total = self.get_item_count(item_type)
        
        if total < quantity:
            return False  # Not enough items
        
        # Remove items from the end of the list first
        for i in reversed(range(len(self.items))):
            if self.items[i] is not None and self.items[i].item_type == item_type:
                if self.items[i].quantity > quantity:
                    # Remove part of the stack
                    self.items[i].quantity -= quantity
                    return True
                else:
                    # Remove the entire stack
                    quantity -= self.items[i].quantity
                    self.items[i] = None
                    
                    if quantity <= 0:
                        return True
        
        return quantity <= 0
    
    def get_item_count(self, item_type: ItemType) -> int:
        """
        Get the total number of items of a specific type in the inventory.
        
        Args:
            item_type: The type of item to count
            
        Returns:
            int: The total number of items of the specified type
        """
        count = 0
        for item in self.items:
            if item is not None and item.item_type == item_type:
                count += item.quantity
        return count
    
    def has_item(self, item_type: ItemType, quantity: int = 1) -> bool:
        """
        Check if the inventory contains at least the specified quantity of an item.
        
        Args:
            item_type: The type of item to check for
            quantity: The minimum number required
            
        Returns:
            bool: True if the inventory has enough of the item
        """
        return self.get_item_count(item_type) >= quantity
    
    def get_selected_item(self) -> Optional[Item]:
        """
        Get the currently selected item in the hotbar.
        
        Returns:
            Optional[Item]: The selected item, or None if the slot is empty
        """
        if 0 <= self.selected_slot < len(self.items):
            return self.items[self.selected_slot]
        return None
    
    def select_slot(self, slot: int) -> bool:
        """
        Select a slot in the hotbar.
        
        Args:
            slot: The slot index to select (0 to hotbar_size-1)
            
        Returns:
            bool: True if the slot was selected, False if out of range
        """
        if 0 <= slot < self.hotbar_size:
            self.selected_slot = slot
            return True
        return False
    
    def next_slot(self) -> None:
        """Select the next slot in the hotbar, wrapping around if needed."""
        self.selected_slot = (self.selected_slot + 1) % self.hotbar_size
    
    def prev_slot(self) -> None:
        """Select the previous slot in the hotbar, wrapping around if needed."""
        self.selected_slot = (self.selected_slot - 1) % self.hotbar_size
    
    def get_empty_slots(self) -> int:
        """
        Get the number of empty slots in the inventory.
        
        Returns:
            int: The number of empty slots
        """
        return sum(1 for item in self.items if item is None)
    
    def is_full(self) -> bool:
        """
        Check if the inventory is full.
        
        Returns:
            bool: True if the inventory is full, False otherwise
        """
        return all(item is not None for item in self.items)
    
    def clear(self) -> None:
        """Clear all items from the inventory."""
        self.items = [None] * self.capacity
    
    def swap_slots(self, slot1: int, slot2: int) -> None:
        """
        Swap the items in two inventory slots.
        
        Args:
            slot1: The index of the first slot
            slot2: The index of the second slot
        """
        if 0 <= slot1 < self.capacity and 0 <= slot2 < self.capacity:
            self.items[slot1], self.items[slot2] = self.items[slot2], self.items[slot1]
    
    def find_item_slot(self, item_type: ItemType) -> int:
        """
        Find the first slot containing an item of the specified type.
        
        Args:
            item_type: The type of item to find
            
        Returns:
            int: The index of the slot, or -1 if not found
        """
        for i, item in enumerate(self.items):
            if item is not None and item.item_type == item_type:
                return i
        return -1
    
    def get_items_of_type(self, item_type: ItemType) -> List[Tuple[int, Item]]:
        """
        Get all items of a specific type in the inventory.
        
        Args:
            item_type: The type of item to find
            
        Returns:
            List[Tuple[int, Item]]: A list of (slot, item) tuples
        """
        return [(i, item) for i, item in enumerate(self.items) 
                if item is not None and item.item_type == item_type]
