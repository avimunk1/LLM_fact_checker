from openai import OpenAI
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from proplexityFinder import process_story
from typing import List
import json 
import pandas as pd  # Add this import at the top
from dotenv import load_dotenv




# Load environment variables at the start of the file
load_dotenv()

def extract_facts_from_text(text: str) -> List[str]:
    """
    Use GPT to extract facts from a given text.
    Each fact will be complete and standalone.
    
    Args:
        text (str): The input text to process
        
    Returns:
        List[str]: List of extracted facts
    """
    
    # Initialize the client
    client = OpenAI()
    
    # System prompt to guide GPT's response
    system_prompt = """You will receive a text in different structures, it could be a short story, a fun fact, or a trivia question. 
Your job is to extract the facts from the text and return a list of facts.
Each fact should:
- Be written as a standalone fact including all the necessary information
- Use full names instead of just surnames
- Include relevant dates, locations, and context
- Be clear and complete without requiring knowledge from other facts

For example:
❌ "Heydrich was assassinated in 1942 in Prague"
✅ "Reinhard Heydrich, a high-ranking Nazi official, was assassinated in 1942 in the neighborhood of Hradčany, Prague"

❌ "The assassination marked a significant act of resistance"
✅ "The assassination of Reinhard Heydrich marked one of the most significant acts of resistance against the Nazi regime during World War II"

Return the facts as a numbered list."""

    try:
        # Make API call to GPT
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract and process the facts
        facts_text = response.choices[0].message.content
        
        # Split the numbered list into individual facts
        facts = []
        for line in facts_text.split('\n'):
            # Remove numbering and whitespace
            line = line.strip()
            if line and any(c.isdigit() for c in line):  # Check if line contains a number
                fact = line.split('.', 1)[-1].strip()  # Get everything after the first period
                if fact:
                    facts.append(fact)
        
        return facts
        
    except Exception as e:
        print(f"Error extracting facts: {e}")
        return []

def verify_fact(fact: str, checkWith: str = "OpenAI") -> tuple[bool, str]:
    """
    Verify a single fact using either OpenAI or Perplexity.
    
    Args:
        fact (str): The fact to verify
        checkWith (str): "OpenAI" or "Perplexity"
        
    Returns:
        tuple[bool, str]: (is_true, explanation if false)
    """
    if checkWith.lower() == "perplexity":
        # Initialize Perplexity client
        api_key = os.getenv('PERPLEXITY_API_KEY')
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment variables")
            
        client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
        
        # Use process_story from perplexityFinder
        result = process_story(fact, client)
        print(f"Perplexity verification result for: {fact}")
        print(f"Result: {result}")
        print("-" * 50)
        
        # For now, return dummy values since we're just printing
        return True, "Using Perplexity (results printed to console)"
        
    else:  # Default OpenAI verification
        client = OpenAI()
        
        # Read system prompt from file
        with open('src/prompts/factCheck.txt', 'r') as file:
            system_prompt = file.read().strip()

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": fact}
                ],
                temperature=0.2
            )
            
            result = response.choices[0].message.content
            is_true = result.lower().startswith('true')
            explanation = '' if is_true else result.replace('False', '').strip()
            
            return is_true, explanation
            
        except Exception as e:
            print(f"Error verifying fact: {e}")
            return False, "Error during verification"
    
# Example usage
if __name__ == "__main__":
    # Configuration parameters
    maxBitsToRead = 100
    bitTypeToUse = "Story"
    checkWith = "OpenAI"  # OpenAI or "Perplexity"
    
    # Prepare DataFrame for results
    results_data = []
    
    # Read and process the JSON file
    with open('/Users/avimunk/Curserprojects/Mapp_utils/files/new.json', 'r') as file:
        data = json.load(file)
    
    # Process each bit_text
    all_facts = []
    bits_processed = 0
    
    # Handle the nested structure
    for item in data:
        if bits_processed >= maxBitsToRead:
            break
            
        place_id = item.get('_id', '')  # Get place_id
        bits = item.get('bits', [])
        for bit in bits:
            if bits_processed >= maxBitsToRead:
                break
            
            if bitTypeToUse and bit.get('bit_type') != bitTypeToUse:
                continue
                
            bit_text = bit.get('bit_txt', '')
            if bit_text:
                facts = extract_facts_from_text(bit_text)
                all_facts.extend(facts)
                
                # Track false facts for this bit
                false_facts_found = False
                bit_results = []
                
                # Verify each fact
                for fact in facts:
                    is_true, explanation = verify_fact(fact, checkWith)
                    if not is_true:
                        false_facts_found = True
                        # Add to results data
                        results_data.append({
                            'place_id': place_id,
                            'bit_id': bit.get('bit_id', ''),
                            'bit_type': bit.get('bit_type', ''),
                            'bit_txt': bit_text,
                            'fact': fact,
                            'is_true': 'False',
                            'description': explanation
                        })
                        
                        # Print false fact
                        if not bit_results:  # Print header only once per bit
                            print(f"\nProcessed text {bits_processed + 1}/{maxBitsToRead}. Found {len(facts)} facts:")
                            print(f"Bit Type: {bit.get('bit_type', 'Unknown')}")
                            print("\nIncorrect facts found:")
                        print(f"\n  {len(bit_results) + 1}. {fact}")
                        print(f"     Verification: ✗ False")
                        print(f"     Explanation: {explanation}")
                        bit_results.append(fact)
                
                if not false_facts_found:
                    print(f"\nProcessed text {bits_processed + 1}/{maxBitsToRead}. Found {len(facts)} facts, all are correct")
                    # Add correct facts to results with empty explanation
                    for fact in facts:
                        results_data.append({
                            'place_id': place_id,
                            'bit_id': bit.get('bit_id', ''),
                            'bit_type': bit.get('bit_type', ''),
                            'bit_txt': bit_text,
                            'fact': fact,
                            'is_true': 'True',
                            'description': ''
                        })
                
                bits_processed += 1

    # Create DataFrame and save to Excel
    df = pd.DataFrame(results_data)
    excel_path = '/Users/avimunk/Curserprojects/Mapp_utils/files/results.xlsx'
    df.to_excel(excel_path, index=False, engine='openpyxl')

    print(f"\n=== Summary ===")
    print(f"Bits processed: {bits_processed}")
    print(f"Total facts extracted: {len(all_facts)}")
    if bitTypeToUse:
        print(f"Bit type filtered: {bitTypeToUse}")
    print(f"Results saved to: {excel_path}")