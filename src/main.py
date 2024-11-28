import json
import os

def extract_data_from_json():
    json_path = "/Users/avimunk/Curserprojects/Mapp_utils/files/fixed.json"
    output_path = "/Users/avimunk/Curserprojects/Mapp_utils/files/new.json"
    
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            content = file.read()
            data = json.loads(content)
            extracted_data = []
            
            # Process each hit in the hits array
            for hit in data['hits']['hits']:
                item = {
                    '_id': hit['_id'],
                    'status': hit['_source'].get('status', ''),
                    'bits': []
                }
                
                # Extract all bits from bit_data array
                if 'bit_data' in hit['_source']:
                    for bit in hit['_source']['bit_data']:
                        bit_item = {
                            'bit_id': bit.get('bit_id', ''),
                            'bit_type': bit.get('bit_type', ''),
                            'bit_txt': bit.get('bit_txt', '')
                        }
                        
                        # Only add right answer for trivia type
                        if bit.get('bit_type', '').lower() == 'trivia':
                            right_answer_index = int(bit.get('rightAnswer', 0))
                            if right_answer_index > 0 and bit.get('answers'):
                                right_answer = bit['answers'][right_answer_index - 1]
                                bit_item['bit_txt'] = f"{bit_item['bit_txt']} The right answer is: {right_answer}"
                        
                        item['bits'].append(bit_item)
                    
                    # Append item if it has any bits
                    if item['bits']:
                        extracted_data.append(item)
            
            # Write to new file with pretty printing
            with open(output_path, 'w', encoding='utf-8') as outfile:
                json.dump(extracted_data, outfile, indent=2, ensure_ascii=False)
                
            print(f"\nSuccessfully created: {output_path}")
                
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_data_from_json()
