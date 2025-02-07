import os
import json
from groq import Groq  # Make sure you have 'groq' library installed
from config import GROQ_API_KEY # Import your API key from config.py

def generate_career_roadmap(education_status, career_goal, resources_available, timeline):
    """
    Generates a structured career roadmap in JSON format using Groq LLM.

    Args:
        education_status (str): User's education status.
        career_goal (str): User's desired career goal.
        resources_available (str): User-provided resources information.
        timeline (int):  Desired timeline in months.

    Returns:
        dict: A JSON-like dictionary representing the career roadmap, or None if there was an error.
    """
    try:
        client = Groq(api_key=GROQ_API_KEY) # Initialize Groq client

        prompt = f"""
        Generate a structured career roadmap in JSON format for someone who wants to become a {career_goal} in {timeline} months.
        Consider their current education status: {education_status} and available resources: {resources_available}.

        The roadmap should be detailed and broken down into months or shorter durations within the given timeline.
        Each duration should have 'topics' and within each topic, there should be a list of 'sub-topics'.
        Also, for each duration, suggest 'resources' like courses, books, or online platforms.

        Example JSON structure:
        {{
          "timeline": {{
            "Month 1-2": {{
              "Topic 1": [
                "Sub-topic 1.1",
                "Sub-topic 1.2"
              ],
              "Topic 2": [
                "Sub-topic 2.1",
                "Sub-topic 2.2"
              ],
              "Resources": [
                "Resource 1",
                "Resource 2"
              ]
            }},
            "Month 3-4": {{
              "Topic 3": [
                "Sub-topic 3.1",
                "Sub-topic 3.2"
              ],
              "Resources": [
                "Resource 3",
                "Resource 4"
              ]
            }}
            // ... more months/durations as needed to fill the timeline
          }}
        }}

        Ensure the roadmap is comprehensive and actionable.  Focus on practical steps and learning objectives.
        """

        response = client.chat.completions.create(
            model="mixtral-8x7b-32768", # Or another suitable Groq model
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" } # Ask for JSON response
        )

        # Parse JSON response
        roadmap_json_str = response.choices[0].message.content
        roadmap_json = json.loads(roadmap_json_str)
        return roadmap_json

    except Exception as e:
        print(f"Error generating career roadmap: {e}")
        return None # Indicate an error occurred


    if __name__ == "__main__":
        # Example usage (for testing ai_agent.py directly)
        test_roadmap = generate_career_roadmap(
            education_status="Bachelor's Degree in Computer Science",
            career_goal="AI Engineer",
            resources_available="10 hours per week, budget for online courses",
            timeline=12
        )

        if test_roadmap:
            print("Generated Roadmap (JSON):")
            print(json.dumps(test_roadmap, indent=2)) # Pretty print JSON for readability
        else:
            print("Failed to generate roadmap.")