#!/usr/bin/env python3
"""
Debug Sentence Length Processing
"""

import re

def debug_sentence_processing():
    # Test the sentence splitting logic
    test_text = "Oh, Emma, wow! A very big animal? Like a big, big dog? Well, how about a puppy? Puppies are great! A dog has many colors! You know what? A puppy can be very fun to play with every single day."
    
    print("Original text:")
    print(test_text)
    print()
    
    # Split sentences using the same regex as the code
    sentences = re.split(r'(?<=[.!?])\s+', test_text)
    print(f"Split into {len(sentences)} sentences:")
    
    simplified_sentences = []
    
    for i, sentence in enumerate(sentences):
        words = sentence.split()
        word_count = len(words)
        print(f"Sentence {i+1}: {word_count} words - '{sentence}'")
        
        if word_count > 8:
            print(f"  -> Too long! Splitting...")
            # Split into smaller chunks
            chunks = [' '.join(words[j:j+6]) + '.' for j in range(0, len(words), 6)]
            print(f"  -> Created {len(chunks)} chunks: {chunks}")
            simplified_sentences.extend(chunks)
        else:
            simplified_sentences.append(sentence)
    
    result_text = ' '.join(simplified_sentences)
    print("\nFinal result:")
    print(result_text)
    
    # Check final sentence lengths
    final_sentences = re.split(r'(?<=[.!?])\s+', result_text)
    print(f"\nFinal sentence analysis:")
    for i, sentence in enumerate(final_sentences):
        words = sentence.split()
        word_count = len(words)
        status = "✅ OK" if word_count <= 8 else "❌ TOO LONG"
        print(f"Sentence {i+1}: {word_count} words {status} - '{sentence}'")

if __name__ == "__main__":
    debug_sentence_processing()