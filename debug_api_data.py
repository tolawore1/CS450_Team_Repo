#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_model_catalog.fetch_repo import fetch_model_data

def debug_api_data():
    print("Fetching BERT model data...")
    api_data = fetch_model_data("bert-base-uncased")
    print("Available fields in api_data:")
    for key, value in api_data.items():
        print(f"  {key}: {value}")
    print()

if __name__ == "__main__":
    debug_api_data()
