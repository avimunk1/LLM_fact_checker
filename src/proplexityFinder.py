import os
from dotenv import load_dotenv
import pandas as pd
from openai import OpenAI

# Load environment variables
load_dotenv()

def process_story(bit_text, client):
    messages = [
        {
            "role": "system",
            "content": (
                """You are an expert in web-based fact-checking, capable of verifying the accuracy of location-specific information. 
                Each story you receive will include a location, specified by country and city names. Your task is to:
                Identify and verify key facts related to the location in each story.
                noting any discrepancies or affirming complete accuracy
                Assign a correctness score from 1 to 5:
                5 = All facts are accurate and relevant to the location.
                1 = All facts are incorrect or irrelevant.
                Additionally, provide a brief explanation for the main and must importent incorrect!! data do not explain what is correct, 
                Format your response exactly like this: Score: X, Explanation: Your single sentence here."""
            ),
        },
        {
            "role": "user",
            "content": f"country: united states, city: new york, {bit_text}"
        },
    ]

    response = client.chat.completions.create(
        model="llama-3.1-sonar-huge-128k-online",
        messages=messages,
    )
    return response.choices[0].message.content

def main():
    # Get API key from environment variable
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        raise ValueError("PERPLEXITY_API_KEY not found in environment variables")
        
    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    
    # Read the entire Excel file
    df = pd.read_excel('/Users/avimunk/Curserprojects/perplixityplayground/files/input_data.xlsx')
    
    # Create new columns for scores, reasons and errors
    df['llma_score'] = None
    df['score_reason'] = None
    df['errors'] = None
    
    # Process each row
    for index, row in df.iterrows():
        bit_text = row['bit_text']
        result = process_story(bit_text, client)
        
        try:
            # Parse response
            score_part = result.split(',')[0]
            score = int(score_part.split(':')[1].strip())
            explanation = result.split(',')[1].strip() if ',' in result else ""
            
            # Store results in DataFrame
            df.at[index, 'llma_score'] = score
            df.at[index, 'score_reason'] = explanation
            
            # Print results (optional)
            print(f"Story {index}: Score: {score}")
            if score < 4:
                print(f"Explanation: {explanation}")
            print("-" * 50)
            
        except Exception as e:
            print(f"Error processing story {index}: {result}")
            df.at[index, 'errors'] = result
            print("-" * 50)
    
    # Save to new Excel file
    output_path = '/Users/avimunk/Curserprojects/perplixityplayground/files/output.xlsx'
    df.to_excel(output_path, index=False)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main()
