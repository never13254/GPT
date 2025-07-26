class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.attack = 10
        self.defense = 5
        self.gold = 50
        self.skills = {
            "Slash": 15,
            "Heavy Strike": 25
        }
        self.inventory = {
            "Potion": 1
        }

    def is_alive(self):
        return self.health > 0

class Monster:
    def __init__(self, name, health, attack, reward):
        self.name = name
        self.health = health
        self.attack = attack
        self.reward = reward

    def is_alive(self):
        return self.health > 0

monsters = [
    Monster("Goblin", 30, 5, 20),
    Monster("Orc", 50, 10, 30),
    Monster("Dragon", 100, 20, 100)
]

shop_items = {
    "Potion": 20,
    "Sword Upgrade": 50
}


def show_stats(player):
    print(f"\n{player.name} Stats:")
    print(f"Health: {player.health}")
    print(f"Attack: {player.attack}")
    print(f"Defense: {player.defense}")
    print(f"Gold: {player.gold}")
    print(f"Inventory: {player.inventory}")


def shop(player):
    while True:
        print("\nWelcome to the shop!")
        for i, (item, price) in enumerate(shop_items.items(), 1):
            print(f"{i}. {item} - {price} gold")
        print("0. Exit Shop")
        choice = input("Choose an item to buy: ")
        if choice == "0":
            break
        try:
            item_choice = list(shop_items.keys())[int(choice) - 1]
        except (IndexError, ValueError):
            print("Invalid choice.")
            continue
        price = shop_items[item_choice]
        if player.gold >= price:
            player.gold -= price
            if item_choice == "Sword Upgrade":
                player.attack += 5
                print("Your sword feels stronger!")
            else:
                player.inventory[item_choice] = player.inventory.get(item_choice, 0) + 1
                print(f"Bought {item_choice}!")
        else:
            print("Not enough gold.")


def fight(player):
    import random
    monster = random.choice(monsters)
    print(f"\nA wild {monster.name} appears!")
    while monster.is_alive() and player.is_alive():
        print(f"\n{monster.name} Health: {monster.health}")
        print(f"Your Health: {player.health}")
        print("1. Attack")
        print("2. Use Skill")
        print("3. Use Potion")
        action = input("Choose your action: ")
        if action == "1":
            damage = max(player.attack - 2, 1)
            monster.health -= damage
            print(f"You attack for {damage} damage!")
        elif action == "2":
            for i, (skill, dmg) in enumerate(player.skills.items(), 1):
                print(f"{i}. {skill} - {dmg} dmg")
            skill_choice = input("Choose skill: ")
            try:
                skill_name = list(player.skills.keys())[int(skill_choice) - 1]
                damage = player.skills[skill_name]
            except (IndexError, ValueError):
                print("Invalid skill.")
                continue
            monster.health -= damage
            print(f"You use {skill_name} for {damage} damage!")
        elif action == "3":
            if player.inventory.get("Potion", 0) > 0:
                player.inventory["Potion"] -= 1
                player.health += 30
                print("You drink a potion and recover 30 health!")
            else:
                print("No potions left!")
                continue
        else:
            print("Invalid action.")
            continue
        if monster.is_alive():
            dmg = monster.attack
            player.health -= dmg
            print(f"{monster.name} attacks you for {dmg}!")
    if player.is_alive():
        player.gold += monster.reward
        print(f"\nYou defeated {monster.name}! You gain {monster.reward} gold.")
    else:
        print("\nYou were defeated...")


if __name__ == "__main__":
    name = input("Enter your hero's name: ")
    player = Player(name)
    while player.is_alive():
        print("\n1. Fight")
        print("2. Shop")
        print("3. Stats")
        print("0. Quit")
        choice = input("Choose an action: ")
        if choice == "1":
            fight(player)
        elif choice == "2":
            shop(player)
        elif choice == "3":
            show_stats(player)
        elif choice == "0":
            break
        else:
            print("Invalid choice.")
    print("Game Over")
