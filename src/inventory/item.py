from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Dict, Any

class ItemType(Enum):
    """Types of items in the game."""
    # Tools
    AXE = auto()
    PICKAXE = auto()
    HOE = auto()
    WATERING_CAN = auto()
    FISHING_ROD = auto()
    
    # Weapons
    SWORD = auto()
    BOW = auto()
    
    # Resources
    WOOD = auto()
    STONE = auto()
    IRON = auto()
    GOLD = auto()
    DIAMOND = auto()
    
    # Crops
    WHEAT = auto()
    CORN = auto()
    CARROT = auto()
    POTATO = auto()
    
    # Seeds
    WHEAT_SEEDS = auto()
    CORN_SEEDS = auto()
    CARROT_SEEDS = auto()
    POTATO_SEEDS = auto()
    
    # Food
    BREAD = auto()
    APPLE = auto()
    FISH = auto()
    COOKED_FISH = auto()
    
    # Other
    COIN = auto()
    KEY = auto()
    TREASURE = auto()

@dataclass
class Item:
    """Represents an item in the game."""
    item_type: ItemType
    quantity: int = 1
    max_stack: int = 99
    data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        # Set max stack size based on item type
        if self.item_type in [
            ItemType.WOOD, ItemType.STONE, ItemType.IRON, ItemType.GOLD, ItemType.DIAMOND,
            ItemType.WHEAT, ItemType.CORN, ItemType.CARROT, ItemType.POTATO,
            ItemType.WHEAT_SEEDS, ItemType.CORN_SEEDS, ItemType.CARROT_SEEDS, ItemType.POTATO_SEEDS,
            ItemType.COIN
        ]:
            self.max_stack = 99
        elif self.item_type in [
            ItemType.AXE, ItemType.PICKAXE, ItemType.HOE, ItemType.WATERING_CAN, ItemType.FISHING_ROD,
            ItemType.SWORD, ItemType.BOW, ItemType.KEY, ItemType.TREASURE
        ]:
            self.max_stack = 1
        else:
            self.max_stack = 16  # Default stack size for other items
    
    def can_stack_with(self, other: 'Item') -> bool:
        """Check if this item can be stacked with another item."""
        return (self.item_type == other.item_type and 
                self.max_stack > 1 and 
                self.quantity + other.quantity <= self.max_stack)
    
    def split(self, amount: int) -> 'Item':
        """Split the item stack into two."""
        if amount <= 0 or amount >= self.quantity:
            raise ValueError("Invalid amount to split")
            
        self.quantity -= amount
        return Item(self.item_type, amount, self.max_stack, self.data)
    
    @property
    def name(self) -> str:
        """Get the display name of the item."""
        return self.item_type.name.lower().replace('_', ' ').title()
    
    @property
    def is_tool(self) -> bool:
        """Check if this item is a tool."""
        return self.item_type in [
            ItemType.AXE, ItemType.PICKAXE, ItemType.HOE, 
            ItemType.WATERING_CAN, ItemType.FISHING_ROD
        ]
    
    @property
    def is_weapon(self) -> bool:
        """Check if this item is a weapon."""
        return self.item_type in [ItemType.SWORD, ItemType.BOW]
    
    @property
    def is_edible(self) -> bool:
        """Check if this item is edible."""
        return self.item_type in [
            ItemType.BREAD, ItemType.APPLE, 
            ItemType.FISH, ItemType.COOKED_FISH
        ]
    
    def use(self, *args, **kwargs) -> bool:
        """Use the item. Returns True if the item was successfully used."""
        # This method should be overridden by subclasses for specific item behaviors
        return False
    
    def __str__(self) -> str:
        """String representation of the item."""
        return f"{self.quantity}x {self.name}" if self.quantity > 1 else self.name
    
    def __eq__(self, other: object) -> bool:
        """Check if two items are of the same type."""
        if not isinstance(other, Item):
            return False
        return self.item_type == other.item_type
    
    def __hash__(self) -> int:
        """Hash the item based on its type."""
        return hash(self.item_type)
