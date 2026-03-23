class Tool:
    def __init__(self, name: str, efficiency: float = 1.0, can_dig: bool = False):
        """Base tool definition used by items."""
        self.name = name
        self.efficiency = efficiency
        self.can_dig = can_dig

    def dig_time(self, hardness: float, base_time: float) -> float:
        """Return the time required to break a tile."""
        if hardness <= 0:
            return 0.0
        efficiency = max(0.1, self.efficiency)
        return max(0.05, base_time * hardness / efficiency)


class MiningTool(Tool):
    def __init__(self, name: str, efficiency: float = 1.0):
        """Tool that can break tiles."""
        super().__init__(name, efficiency=efficiency, can_dig=True)


class Weapon(Tool):
    def __init__(self, name: str, efficiency: float = 1.0):
        """Weapon that does not break tiles by default."""
        super().__init__(name, efficiency=efficiency, can_dig=False)
