from click import prompt
import google.generativeai as genai
from google.generativeai.types import Tool  # This should now be found by 0.7.0
from app.config import settings
from app.models.gemini_models import (
    InitialTripSuggestions,
    OptimizedItinerary,
    TripPlanningAnalysis,
    SuggestedLocation,
    OptimizedItineraryStep,
)
from typing import List, Dict, Any, Literal
import json
from datetime import datetime
from pydantic import BaseModel

genai.configure(api_key=settings.GOOGLE_API_KEY)


class GeminiService:
    def __init__(self):
        self.generation_model = genai.GenerativeModel("gemini-1.5-pro-latest")
        self.vision_model = genai.GenerativeModel("gemini-pro-vision")
        self.chat_model = genai.GenerativeModel("gemini-1.5-pro-latest")

    def _extract_values_from_schema_response(
        self, response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract actual values from Gemini's schema-style response format.
        Converts from {"field": {"value": "actual_value"}} to {"field": "actual_value"}
        """
        if not isinstance(response_data, dict):
            return response_data

        # Check if this looks like a schema response (has "properties" key)
        if "properties" in response_data:
            extracted = {}
            properties = response_data["properties"]

            for field_name, field_data in properties.items():
                if isinstance(field_data, dict) and "value" in field_data:
                    extracted[field_name] = field_data["value"]
                else:
                    # Fallback for fields that don't have the schema format
                    extracted[field_name] = field_data

            return extracted

        # If it's not a schema response, return as-is
        return response_data

    async def _generate_content_with_tools(
        self, prompt: str, output_model: BaseModel, tools: List[Tool] = None
    ):
        """Helper to generate content with tools and parse output into a Pydantic model."""
        try:
            tool_config_param = (
                {"function_calling_config": {"mode": "AUTO"}} if tools else None
            )

            response = self.generation_model.generate_content(
                prompt,
                tools=tools,
                tool_config=tool_config_param,
            )

            content_text = response.text  # This should not cause an await error
            print(
                f"Attempting to parse JSON for {output_model.__name__}:\n{content_text}"
            )

            # Parse JSON and extract values if it's a schema response
            parsed_data = json.loads(content_text)
            extracted_data = self._extract_values_from_schema_response(parsed_data)

            return output_model.model_validate(extracted_data)
        except Exception as e:
            print(
                f"Error generating content with tools for {output_model.__name__}: {e}"
            )
            print(f"Prompt that failed: {prompt}")
            if "response" in locals() and hasattr(response, "text"):
                print(f"Raw response text (may not be valid JSON): {response.text}")
            raise

    async def _generate_content_with_json_parsing(
        self, prompt: str, output_model: BaseModel
    ):
        """Helper to generate content with JSON parsing and parse output into a Pydantic model."""
        try:
            # Add JSON schema and format instructions to the prompt
            json_schema = output_model.model_json_schema()
            enhanced_prompt = f"""
{prompt}

Please respond with a valid JSON object that matches this exact schema:
{json.dumps(json_schema, indent=2)}

IMPORTANT: 
- Your response must be valid JSON only, with no additional text or formatting.
- Do not include schema definitions or metadata.
- Return only the actual field values, not wrapped in "value" properties.
- For example, return {{"weather_summary": "Sunny and warm"}} not {{"weather_summary": {{"value": "Sunny and warm"}}}}

Example of correct format:
{{
  "weather_summary": "Sunny with temperatures around 75°F",
  "clothing_suggestion": "Light clothing recommended",
  "carry_umbrella": false,
  "general_money_tips": "Consider purchasing a city pass",
  "transportation_tips": "Use public transit",
  "other_carry_items": ["sunscreen", "water bottle"],
  "location_info": [{{"name": "Example Location", "typical_hours": "9 AM - 5 PM", "quick_fact": "Famous for..."}}]
}}
"""

            response = self.generation_model.generate_content(enhanced_prompt)
            content_text = response.text.strip()

            # Clean up the response in case there's extra formatting
            if content_text.startswith("```json"):
                content_text = content_text[7:]  # Remove ```json
            if content_text.endswith("```"):
                content_text = content_text[:-3]  # Remove ```
            content_text = content_text.strip()

            print(
                f"Attempting to parse JSON for {output_model.__name__}:\n{content_text}"
            )

            # Parse JSON and extract values if it's a schema response
            parsed_data = json.loads(content_text)
            extracted_data = self._extract_values_from_schema_response(parsed_data)

            return output_model.model_validate(extracted_data)
        except json.JSONDecodeError as e:
            print(f"JSON decode error for {output_model.__name__}: {e}")
            print(f"Raw response text: {content_text}")  # <--- Keep this active
            raise
        except Exception as e:
            print(
                f"Error generating content with JSON parsing for {output_model.__name__}: {e}"
            )
            print(f"Prompt that failed: {prompt}")
            if "response" in locals() and hasattr(response, "text"):
                print(f"Raw response text: {response.text}")  # <--- Keep this active
            raise

    async def get_initial_trip_suggestions(
        self,
        city: str,
        interests: List[str],
        pace: Literal["fast-paced", "relaxed"],
        trip_date: datetime,
        weather_data: Dict[str, Any],
    ) -> InitialTripSuggestions:
        formatted_date = trip_date.strftime("%A, %B %d, %Y")
        current_time_str = datetime.now().strftime("%I:%M %p %Z")
        weather_summary_for_gemini = weather_data.get(
            "summary", "Weather information not available."
        )

        prompt = (
            f"You are an AI travel planning companion. The user wants to plan a 1-day trip in {city} "
            f"on {formatted_date}. The current local time in Chicago is {current_time_str}. "
            f"Their primary interests are: {', '.join(interests)}. They prefer a '{pace}' pace. "
            f"The weather forecast for {city} on {formatted_date} is: {weather_summary_for_gemini}. "
            f"Suggest 3-5 distinct, highly-rated locations/activities that fit these preferences and are "
            f"typically open and feasible for a day trip. For each suggestion, provide: "
            f"name, type (e.g., museum, park, restaurant, landmark, tour, other), a brief description, "
            f"estimated visit time in minutes, typical admission cost in USD (null if free), "
            f"clear reasons for suggestion, and a summary of typical operating hours. "
            f"Also, give general weather and clothing advice for that day based on the provided weather data, "
            f"and indicate if an umbrella or rain gear is recommended."
        )

        return await self._generate_content_with_json_parsing(
            prompt, output_model=InitialTripSuggestions
        )

    async def get_detailed_trip_analysis(
        self,
        city: str,
        trip_date: datetime,
        selected_locations: List[Dict[str, Any]],
        return_time: str,
        user_preferences: Dict[str, Any],
        weather_data: Dict[str, Any],
    ) -> TripPlanningAnalysis:
        formatted_date = trip_date.strftime("%A, %B %d, %Y")
        current_time_str = datetime.now().strftime("%I:%M %p %Z")
        weather_summary_for_gemini = weather_data.get(
            "summary", "Weather information not available."
        )

        locations_str = "\n".join(
            [
                f"- {loc.get('name')} (Type: {loc.get('type', 'Unknown')}, Est. Visit: {loc.get('estimated_time_spent_minutes', 'N/A')} mins)"
                for loc in selected_locations
            ]
        )
        preferences_str = ", ".join([f"{k}: {v}" for k, v in user_preferences.items()])

        prompt = (
            f"You are an AI travel planning companion. The user is planning a 1-day trip to {city} "
            f"on {formatted_date}. They want to return home by {return_time}. "
            f"Their selected locations are:\n{locations_str}\n"
            f"Their preferences include: {preferences_str}. "
            f"Current local time in Chicago is {current_time_str}. "
            f"Weather forecast for {city} on {formatted_date}: {weather_summary_for_gemini}. "
            f"Provide a comprehensive analysis including:\n"
            f"- A detailed summary of the weather for {formatted_date} in {city} (temperature, conditions, any warnings like high UV) based on the provided weather data.\n"
            f"- Detailed clothing suggestions based on the weather.\n"
            f"- Whether an umbrella or rain gear is recommended based on the weather forecast.\n"
            f"- Estimated costs for gas (if driving from suburbs, include parking downtown, provide a realistic range for Chicago for a day). "
            f"and public transit (e.g., typical 1-day pass cost and single ride fare).\n"
            f"- Estimated ride-share costs for typical short trips between downtown attractions (e.g., 3-4 rides).\n"
            f"- General money-saving tips for Chicago.\n"
            f"- General transportation tips for the chosen modes (e.g., advice on CTA passes, parking apps if driving, ride-share peak times).\n"
            f"- Other essential items to carry (e.g., sunscreen, water bottle, portable phone charger, comfortable shoes).\n"
            f"- For each selected location (from the list provided), provide brief, relevant information like typical operating hours, "
            f"and a quick fact or two, based on common knowledge for these well-known Chicago spots."
        )

        return await self._generate_content_with_json_parsing(
            prompt, output_model=TripPlanningAnalysis
        )

    async def optimize_itinerary(
        self,
        city: str,
        trip_date: datetime,
        selected_locations: List[Dict[str, Any]],
        return_time: str,
        user_preferences: Dict[str, Any],
    ) -> OptimizedItinerary:
        formatted_date = trip_date.strftime("%A, %B %d, %Y")
        current_time_str = datetime.now().strftime("%I:%M %p %Z")

        locations_str = "\n".join(
            [
                f"- {loc.get('name')} (Type: {loc.get('type', 'attraction')}, Est. Visit: {loc.get('estimated_time_spent_minutes', 0)} mins, Admission: ${loc.get('admission_cost_usd', '0.0')} USD)"
                for loc in selected_locations
            ]
        )
        preferences_str = ", ".join([f"{k}: {v}" for k, v in user_preferences.items()])

        prompt = (
            f"You are an AI travel planning companion. The user is planning a 1-day trip to {city} "
            f"on {formatted_date}. They want to return home by {return_time}. "
            f"Their preferred pace is '{user_preferences.get('pace', 'relaxed')}'. "
            f"Their selected locations are:\n{locations_str}\n"
            f"Current local time in Chicago is {current_time_str}. "
            f"Considering these, and assuming the day starts around 9:00 AM, create a detailed, optimized itinerary. "
            f"For each step, include: activity description, exact start time, exact end time, location name, address (if available and relevant), "
            f"estimated travel time to the next step (in minutes), recommended mode of transport (walk, public_transit, ride_share, drive), "
            f"and any important notes (e.g., 'Buy tickets online', 'Lunch break here'). "
            f"Ensure to build in realistic buffer time for transitions, meals (explicitly add 'Lunch' and 'Dinner' activities), and short breaks. "
            f"The dinner activity should be for 'deep-dish pizza'. "
            f"Assess the overall feasibility of covering all selected locations and returning by {return_time}. "
            f"Feasibility status must be one of: 'possible', 'tight_but_possible', or 'not_possible'. "
            f"Provide notes on feasibility, especially if it's tight. "
            f"Calculate the total estimated cost for admissions based on the provided admission costs. "
            f"Also give a general estimate for food and local transport combined for the day. "
            f"Finally, calculate the total estimated travel time (sum of all estimated_travel_time_minutes) and total activity time (sum of all estimated_time_spent_minutes) for the day."
        )

        return await self._generate_content_with_json_parsing(
            prompt, output_model=OptimizedItinerary
        )
