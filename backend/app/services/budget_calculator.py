from typing import Dict, Any, List

class BudgetCalculator:
    """
    Service to estimate various costs for a trip.
    (Placeholder implementation - real data would come from APIs or historical averages).
    """
    def __init__(self):
        pass

    async def estimate_food_costs(self, num_meals: int, budget_range: str) -> Dict[str, float]:
        """Estimates food costs based on number of meals and budget range."""
        per_meal_cost = {
            "budget": 15,  # e.g., fast food, casual diner
            "mid-range": 30, # e.g., sit-down restaurant
            "luxury": 70   # e.g., fine dining
        }
        cost = num_meals * per_meal_cost.get(budget_range, 30)
        return {"estimated_food_cost_usd": float(cost)}

    async def estimate_transport_costs(self, mode: str, distance_miles: float = 0) -> Dict[str, float]:
        """Estimates transportation costs based on mode and distance."""
        if mode == "driving":
            # Very rough estimate for Chicago: gas + parking downtown
            gas_cost = distance_miles * 0.15 # assuming average car MPG and gas price
            parking_cost = 40.0 # Average downtown Chicago parking for a day
            return {"estimated_gas_cost_usd": gas_cost, "estimated_parking_cost_usd": parking_cost}
        elif mode == "public_transit":
            # Assume 1-day pass for simplicity
            return {"estimated_public_transit_cost_usd": 5.0}
        elif mode == "ride_share":
            # Assume average short ride is $15, maybe 3-4 rides
            return {"estimated_ride_share_cost_usd": 50.0}
        elif mode == "walking":
            return {"estimated_walking_cost_usd": 0.0}
        return {}

    async def calculate_total_costs(
        self,
        selected_locations: List[Dict[str, Any]],
        num_meals: int,
        budget_range: str,
        preferred_transport_modes: List[str]
    ) -> Dict[str, Any]:
        """Calculates total estimated costs for the trip."""
        total_admission_cost = sum(loc.get('admission_cost_usd', 0.0) for loc in selected_locations if loc.get('admission_cost_usd') is not None)
        
        food_costs = await self.estimate_food_costs(num_meals, budget_range)
        
        transport_costs = {}
        # This is simplified; real logic would depend on actual routes
        for mode in preferred_transport_modes:
            transport_costs.update(await self.estimate_transport_costs(mode)) # Combine estimates
        
        total_estimated_cost = total_admission_cost + food_costs.get("estimated_food_cost_usd", 0) + \
                               sum(transport_costs.values())
        
        return {
            "total_admission_cost_usd": total_admission_cost,
            "food_costs": food_costs,
            "transport_costs": transport_costs,
            "overall_total_estimated_cost_usd": total_estimated_cost
        }