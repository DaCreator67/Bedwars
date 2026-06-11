"""
LEMONADE EMPIRE - A comprehensive lemonade selling game
Inspired by the Roblox game "Sell Lemons" with expanded features
"""

import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from enum import Enum


class ItemQuality(Enum):
    """Quality levels for products"""
    POOR = 0.5
    NORMAL = 1.0
    GOOD = 1.5
    EXCELLENT = 2.0
    PREMIUM = 3.0


class BusinessType(Enum):
    """Types of businesses available"""
    LEMONADE_STAND = "Lemonade Stand"
    ICE_CREAM_SHOP = "Ice Cream Shop"
    SMOOTHIE_BAR = "Smoothie Bar"
    JUICE_CAFE = "Juice Cafe"
    LUXURY_LOUNGE = "Luxury Lounge"


class GameEvent:
    """Events that can occur during gameplay"""
    def __init__(self, name: str, effect: float, probability: float = 0.1):
        self.name = name
        self.effect = effect  # Multiplier effect on sales
        self.probability = probability
    
    def trigger(self) -> bool:
        return random.random() < self.probability


class Product:
    """Represents a product to sell"""
    def __init__(self, name: str, base_cost: float, base_price: float, quality: ItemQuality = ItemQuality.NORMAL):
        self.name = name
        self.base_cost = base_cost
        self.base_price = base_price * quality.value
        self.quality = quality
        self.inventory = 0
    
    def calculate_profit(self) -> float:
        """Calculate profit per unit"""
        return self.base_price - self.base_cost
    
    def __repr__(self):
        return f"{self.name} (Quality: {self.quality.name}) - Sells for ${self.base_price:.2f}"


class Upgrade:
    """Represents an upgrade for the business"""
    def __init__(self, name: str, cost: float, effect_type: str, effect_value: float, business_type: BusinessType = None):
        self.name = name
        self.cost = cost
        self.effect_type = effect_type  # e.g., "sales_boost", "cost_reduction", "production_speed"
        self.effect_value = effect_value
        self.purchased = False
        self.level = 0
        self.business_type = business_type
    
    def __repr__(self):
        status = "✓ PURCHASED" if self.purchased else f"${self.cost:.2f}"
        return f"{self.name} ({self.effect_type}) - {status}"


class SecretPass:
    """Secret code that unlocks special features"""
    def __init__(self, code: str, name: str, rewards: Dict, description: str = ""):
        self.code = code
        self.name = name
        self.rewards = rewards  # e.g., {"money": 1000, "unlock": "premium_items"}
        self.description = description
        self.used = False
    
    def activate(self, player: 'Player') -> bool:
        """Activate the secret pass"""
        if self.used:
            return False
        
        for reward_type, value in self.rewards.items():
            if reward_type == "money":
                player.money += value
            elif reward_type == "unlock":
                player.unlocked_features.add(value)
            elif reward_type == "items":
                for item_name, amount in value.items():
                    if item_name in player.products:
                        player.products[item_name].inventory += amount
        
        self.used = True
        return True


class Player:
    """Main player character"""
    def __init__(self, name: str):
        self.name = name
        self.money = 100.0  # Starting money
        self.level = 1
        self.experience = 0
        self.exp_to_level = 100
        
        # Business management
        self.current_business = BusinessType.LEMONADE_STAND
        self.products: Dict[str, Product] = {}
        self.upgrades: Dict[str, Upgrade] = {}
        self.unlocked_features = set()
        
        # Statistics
        self.total_sales = 0
        self.items_sold = 0
        self.total_profit = 0.0
        self.playtime_minutes = 0
        
        # Unlocked content
        self.unlocked_businesses = {BusinessType.LEMONADE_STAND}
        self.unlocked_secret_passes: List[SecretPass] = []
        
        # Initialize starting products
        self._initialize_products()
    
    def _initialize_products(self):
        """Initialize products for lemonade stand"""
        self.products = {
            "lemonade": Product("Regular Lemonade", 0.20, 1.50, ItemQuality.NORMAL),
            "premium_lemonade": Product("Premium Lemonade", 0.50, 3.50, ItemQuality.GOOD),
            "exotic_lemonade": Product("Exotic Lemonade", 1.00, 7.00, ItemQuality.EXCELLENT),
        }
        
        # Add starting inventory
        self.products["lemonade"].inventory = 20
    
    def add_money(self, amount: float):
        """Add money to player's balance"""
        self.money += amount
        if self.money < 0:
            self.money = 0
    
    def add_experience(self, amount: int):
        """Add experience and handle leveling"""
        self.experience += amount
        while self.experience >= self.exp_to_level:
            self.level_up()
    
    def level_up(self):
        """Level up the player"""
        self.experience -= self.exp_to_level
        self.level += 1
        self.exp_to_level = int(self.exp_to_level * 1.1)
        print(f"\n🎉 LEVEL UP! You are now level {self.level}!")
        print(f"Experience needed for next level: {self.exp_to_level}")
    
    def switch_business(self, business_type: BusinessType) -> bool:
        """Switch to a different business type"""
        if business_type not in self.unlocked_businesses:
            print(f"❌ You haven't unlocked {business_type.value} yet!")
            return False
        
        self.current_business = business_type
        print(f"✓ Switched to {business_type.value}")
        return True
    
    def get_status(self) -> str:
        """Get current player status"""
        status = f"""
╔════════════════════════════════════════╗
║      LEMONADE EMPIRE - STATUS REPORT   ║
╚════════════════════════════════════════╝

Player: {self.name}
Level: {self.level} | EXP: {self.experience}/{self.exp_to_level}
💰 Money: ${self.money:.2f}
📊 Current Business: {self.current_business.value}

STATISTICS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 Total Sales: {self.total_sales}
📦 Items Sold: {self.items_sold}
💵 Total Profit: ${self.total_profit:.2f}
⏱️  Playtime: {self.playtime_minutes} minutes

INVENTORY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for product_name, product in self.products.items():
            status += f"  • {product.name}: {product.inventory} units (${product.base_price:.2f} each)\n"
        
        return status


class GameEngine:
    """Main game engine"""
    
    # Secret passes database
    SECRET_PASSES = [
        SecretPass("LEMONADE_TYCOON", "Tycoon Starter", {"money": 5000}, "Starting boost for business tycoons"),
        SecretPass("GOLDEN_RECIPE", "Golden Recipe", {"unlock": "premium_items"}, "Unlock premium product recipes"),
        SecretPass("TIME_TRAVELER", "Time Traveler", {"money": 1000, "unlock": "time_multiplier"}, "Unlock time speed boost"),
        SecretPass("BUSINESS_EMPIRE", "Empire Builder", {"unlock": "all_businesses"}, "Unlock all business types"),
        SecretPass("ENDLESS_SUPPLIES", "Endless Supplies", {"items": {"lemonade": 100, "premium_lemonade": 50}}, "Stock up on products"),
        SecretPass("LUCKY_CHARM", "Lucky Charm", {"unlock": "luck_multiplier"}, "Increase random event chances"),
        SecretPass("VIP_ACCESS", "VIP Access", {"unlock": "vip_features"}, "Unlock exclusive VIP features"),
        SecretPass("SPEED_RUN", "Speed Racer", {"unlock": "speed_boost", "money": 2000}, "Unlock 2x production speed"),
    ]
    
    # Game events
    EVENTS = [
        GameEvent("🌞 Hot Day!", 1.5, 0.15),
        GameEvent("☔ Rainy Day", 0.5, 0.10),
        GameEvent("🎉 Festival", 2.0, 0.08),
        GameEvent("😤 Equipment Malfunction", 0.7, 0.12),
        GameEvent("📺 Viral Marketing", 3.0, 0.05),
        GameEvent("🏆 Competition Wins", 1.8, 0.10),
        GameEvent("📉 Market Crash", 0.4, 0.08),
        GameEvent("🤝 Partnership Formed", 1.6, 0.09),
    ]
    
    def __init__(self, player: Player):
        self.player = player
        self.running = True
        self.session_start = datetime.now()
        self.current_event = None
    
    def get_dynamic_customer_count(self) -> int:
        """Calculate number of customers based on various factors"""
        base_customers = random.randint(5, 20)
        
        # Business type affects customer count
        business_multipliers = {
            BusinessType.LEMONADE_STAND: 1.0,
            BusinessType.ICE_CREAM_SHOP: 1.3,
            BusinessType.SMOOTHIE_BAR: 1.2,
            BusinessType.JUICE_CAFE: 1.1,
            BusinessType.LUXURY_LOUNGE: 0.8,
        }
        
        multiplier = business_multipliers.get(self.player.current_business, 1.0)
        
        # Level affects customer count
        level_bonus = 1.0 + (self.player.level * 0.05)
        
        # Check for active events
        event_multiplier = 1.0
        if self.current_event:
            event_multiplier = self.current_event.effect
        
        customers = int(base_customers * multiplier * level_bonus * event_multiplier)
        return max(1, customers)
    
    def check_for_events(self) -> str:
        """Check if an event occurs"""
        for event in self.EVENTS:
            if event.trigger():
                self.current_event = event
                return f"\n⚡ EVENT: {event.name}\n   Sales multiplier: x{event.effect}"
        
        self.current_event = None
        return ""
    
    def sell_product(self, product_name: str) -> Tuple[bool, str]:
        """Attempt to sell a product"""
        if product_name not in self.player.products:
            return False, "❌ Product not found!"
        
        product = self.player.products[product_name]
        
        if product.inventory == 0:
            return False, f"❌ Out of stock: {product.name}"
        
        # Get customer count
        customers = self.get_dynamic_customer_count()
        
        # Check for events
        event_message = self.check_for_events()
        
        # Calculate sales
        event_multiplier = self.current_event.effect if self.current_event else 1.0
        
        # Some customers might not buy
        actual_sales = int(customers * random.uniform(0.5, 1.0))
        actual_sales = min(actual_sales, product.inventory)  # Can't sell more than inventory
        
        if actual_sales == 0:
            return False, f"😞 No customers interested in {product.name} today..."
        
        revenue = actual_sales * product.base_price * event_multiplier
        profit = actual_sales * product.calculate_profit() * event_multiplier
        
        # Update inventory
        product.inventory -= actual_sales
        
        # Update stats
        self.player.money += revenue
        self.player.total_sales += actual_sales
        self.player.items_sold += actual_sales
        self.player.total_profit += profit
        self.player.add_experience(actual_sales * 2)
        
        message = f"""
{'='*50}
📊 SALES REPORT
{'='*50}
Product: {product.name}
Customers Today: {customers} 💼
Units Sold: {actual_sales} ✓
Revenue: ${revenue:.2f}
Profit: ${profit:.2f}
Remaining Inventory: {product.inventory}
{event_message}
{'='*50}
"""
        return True, message
    
    def buy_product(self, product_name: str, quantity: int) -> Tuple[bool, str]:
        """Buy stock for a product"""
        if product_name not in self.player.products:
            return False, "❌ Product not found!"
        
        product = self.player.products[product_name]
        total_cost = product.base_cost * quantity
        
        if self.player.money < total_cost:
            return False, f"❌ Insufficient funds! Need ${total_cost:.2f}, have ${self.player.money:.2f}"
        
        self.player.money -= total_cost
        product.inventory += quantity
        
        return True, f"✓ Purchased {quantity} {product.name}(s) for ${total_cost:.2f}"
    
    def buy_upgrade(self, upgrade_name: str) -> Tuple[bool, str]:
        """Purchase an upgrade"""
        if upgrade_name not in self.player.upgrades:
            return False, "❌ Upgrade not found!"
        
        upgrade = self.player.upgrades[upgrade_name]
        
        if upgrade.purchased:
            return False, f"❌ You already own {upgrade.name}!"
        
        if self.player.money < upgrade.cost:
            return False, f"❌ Insufficient funds! Need ${upgrade.cost:.2f}, have ${self.player.money:.2f}"
        
        self.player.money -= upgrade.cost
        upgrade.purchased = True
        upgrade.level = 1
        
        return True, f"✓ Purchased {upgrade.name}!"
    
    def redeem_secret_pass(self, code: str) -> Tuple[bool, str]:
        """Redeem a secret pass"""
        for secret_pass in self.SECRET_PASSES:
            if secret_pass.code.lower() == code.lower():
                if secret_pass.used:
                    return False, "❌ This code has already been used!"
                
                if secret_pass.activate(self.player):
                    self.player.unlocked_secret_passes.append(secret_pass)
                    
                    # Handle special unlocks
                    if "all_businesses" in secret_pass.rewards.get("unlock", []):
                        self.player.unlocked_businesses = set(BusinessType)
                    
                    message = f"""
✨ SECRET PASS ACTIVATED! ✨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏆 {secret_pass.name}
📝 {secret_pass.description}

REWARDS CLAIMED:
"""
                    for reward_type, value in secret_pass.rewards.items():
                        if reward_type == "money":
                            message += f"  💰 +${value}\n"
                        elif reward_type == "unlock":
                            message += f"  🔓 Unlocked: {value}\n"
                        elif reward_type == "items":
                            for item, amount in value.items():
                                message += f"  📦 +{amount} {item}\n"
                    
                    return True, message
                else:
                    return False, "❌ Error activating code!"
        
        return False, "❌ Invalid secret code!"
    
    def list_secret_passes(self) -> str:
        """List available secret passes"""
        message = """
╔════════════════════════════════════════╗
║       AVAILABLE SECRET PASSES          ║
╚════════════════════════════════════════╝

"""
        for i, secret_pass in enumerate(self.SECRET_PASSES, 1):
            status = "✓ USED" if secret_pass.used else "🔒 AVAILABLE"
            message += f"{i}. {secret_pass.code} - {secret_pass.name} ({status})\n"
            message += f"   📝 {secret_pass.description}\n\n"
        
        return message
    
    def show_menu(self) -> str:
        """Display main game menu"""
        menu = f"""
╔════════════════════════════════════════╗
║     LEMONADE EMPIRE - MAIN MENU        ║
╚════════════════════════════════════════╝

Current Balance: ${self.player.money:.2f}
Level: {self.player.level} ({self.player.experience}/{self.player.exp_to_level} EXP)

1. 🏪 SELL PRODUCTS
2. 📦 BUY INVENTORY
3. 🛠️  VIEW UPGRADES
4. 💼 SWITCH BUSINESS
5. 📊 VIEW STATUS
6. 🔑 REDEEM SECRET PASS
7. 📋 LIST SECRET PASSES
8. ❓ HELP
9. 🚪 QUIT

Select an option (1-9): """
        return menu
    
    def show_help(self) -> str:
        """Display help information"""
        return """
╔════════════════════════════════════════╗
║           GAME HELP SECTION            ║
╚════════════════════════════════════════╝

🎮 HOW TO PLAY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Buy inventory of products
2. Sell products to customers
3. Earn money and experience
4. Level up to unlock new features
5. Purchase upgrades to boost sales
6. Redeem secret codes for rewards

💡 TIPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Higher quality products sell for more
• Events affect daily sales randomly
• Level up to attract more customers
• Secret passes unlock special rewards
• Multiple businesses are available

🔑 SECRET CODES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Try entering secret codes for rewards!
Check "LIST SECRET PASSES" for available codes.
"""
    
    def run_game_loop(self):
        """Main game loop"""
        print("\n" + "="*50)
        print("🍋 WELCOME TO LEMONADE EMPIRE 🍋")
        print("="*50)
        print(f"Welcome, {self.player.name}!")
        print(f"Starting capital: ${self.player.money:.2f}")
        print("="*50 + "\n")
        
        while self.running:
            try:
                choice = input(self.show_menu()).strip()
                
                if choice == "1":
                    self.sell_menu()
                elif choice == "2":
                    self.buy_inventory_menu()
                elif choice == "3":
                    self.upgrades_menu()
                elif choice == "4":
                    self.switch_business_menu()
                elif choice == "5":
                    print(self.player.get_status())
                elif choice == "6":
                    self.redeem_code_menu()
                elif choice == "7":
                    print(self.list_secret_passes())
                elif choice == "8":
                    print(self.show_help())
                elif choice == "9":
                    self.quit_game()
                else:
                    print("❌ Invalid option! Please select 1-9.")
                
                time.sleep(0.5)
            
            except KeyboardInterrupt:
                print("\n\n⚠️  Game interrupted!")
                self.quit_game()
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def sell_menu(self):
        """Handle product selling"""
        print("\n" + "="*50)
        print("🏪 SELL PRODUCTS")
        print("="*50)
        
        for i, (key, product) in enumerate(self.player.products.items(), 1):
            print(f"{i}. {product} | Stock: {product.inventory}")
        
        print(f"{len(self.player.products) + 1}. Back to menu")
        
        try:
            choice = int(input("\nSelect product to sell (number): ")) - 1
            
            if choice == len(self.player.products):
                return
            
            products_list = list(self.player.products.keys())
            if 0 <= choice < len(products_list):
                success, message = self.sell_product(products_list[choice])
                print(message)
            else:
                print("❌ Invalid selection!")
        
        except ValueError:
            print("❌ Please enter a valid number!")
    
    def buy_inventory_menu(self):
        """Handle inventory purchasing"""
        print("\n" + "="*50)
        print("📦 BUY INVENTORY")
        print("="*50)
        print(f"Current Balance: ${self.player.money:.2f}\n")
        
        for i, (key, product) in enumerate(self.player.products.items(), 1):
            print(f"{i}. {product}")
            print(f"   Cost per unit: ${product.base_cost:.2f}")
            print(f"   Current stock: {product.inventory}\n")
        
        print(f"{len(self.player.products) + 1}. Back to menu")
        
        try:
            choice = int(input("Select product to buy (number): ")) - 1
            
            if choice == len(self.player.products):
                return
            
            products_list = list(self.player.products.keys())
            if 0 <= choice < len(products_list):
                quantity = int(input("How many units to buy? "))
                
                if quantity < 1:
                    print("❌ Quantity must be at least 1!")
                    return
                
                success, message = self.buy_product(products_list[choice], quantity)
                print(message)
            else:
                print("❌ Invalid selection!")
        
        except ValueError:
            print("❌ Please enter valid numbers!")
    
    def upgrades_menu(self):
        """Handle upgrades"""
        print("\n" + "="*50)
        print("🛠️  UPGRADES")
        print("="*50)
        print(f"Current Balance: ${self.player.money:.2f}\n")
        
        if not self.player.upgrades:
            print("No upgrades available yet. Keep playing to unlock more!")
            return
        
        for i, (key, upgrade) in enumerate(self.player.upgrades.items(), 1):
            print(f"{i}. {upgrade}")
        
        print(f"{len(self.player.upgrades) + 1}. Back to menu")
    
    def switch_business_menu(self):
        """Handle business switching"""
        print("\n" + "="*50)
        print("💼 SWITCH BUSINESS")
        print("="*50)
        print(f"Current Business: {self.player.current_business.value}\n")
        print("Available Businesses:\n")
        
        available = list(self.player.unlocked_businesses)
        for i, business in enumerate(available, 1):
            locked = "🔓 Unlocked" if business in self.player.unlocked_businesses else "🔒 Locked"
            print(f"{i}. {business.value} ({locked})")
        
        print(f"{len(available) + 1}. Back to menu")
        
        try:
            choice = int(input("\nSelect business to switch to (number): ")) - 1
            
            if choice == len(available):
                return
            
            if 0 <= choice < len(available):
                self.player.switch_business(available[choice])
            else:
                print("❌ Invalid selection!")
        
        except ValueError:
            print("❌ Please enter a valid number!")
    
    def redeem_code_menu(self):
        """Handle secret code redemption"""
        print("\n" + "="*50)
        print("🔑 REDEEM SECRET PASS")
        print("="*50)
        code = input("Enter secret code: ").strip()
        
        success, message = self.redeem_secret_pass(code)
        print(message)
    
    def quit_game(self):
        """End the game"""
        session_duration = (datetime.now() - self.session_start).total_seconds() / 60
        
        print("\n" + "="*50)
        print("🎮 GAME ENDED")
        print("="*50)
        print(f"\nFinal Statistics:")
        print(f"  Level Reached: {self.player.level}")
        print(f"  Total Profit: ${self.player.total_profit:.2f}")
        print(f"  Items Sold: {self.player.items_sold}")
        print(f"  Final Balance: ${self.player.money:.2f}")
        print(f"  Playtime: {session_duration:.1f} minutes")
        print("\nThanks for playing Lemonade Empire! 🍋")
        print("="*50)
        
        self.running = False


def main():
    """Main entry point"""
    print("\n" + "="*50)
    print("🍋 LEMONADE EMPIRE STARTUP 🍋")
    print("="*50)
    
    player_name = input("Enter your player name: ").strip() or "Player"
    player = Player(player_name)
    
    game = GameEngine(player)
    game.run_game_loop()


if __name__ == "__main__":
    main()
