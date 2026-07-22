"""
Test simple de l'endpoint POST /api/predict/cnn
─────────────────────────────────────────────────
Usage :
  python test_predict.py <chemin_image> [base_url]

Équivalent curl :
  curl -X POST -F "image=@chemin/vers/image.jpg" http://localhost:5000/api/predict/cnn
"""

import sys
import requests

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage : python test_predict.py <chemin_image> [base_url]")
        raise SystemExit(1)

    image_path = sys.argv[1]
    base_url   = sys.argv[2] if len(sys.argv) > 2 else 'http://localhost:5000'

    with open(image_path, 'rb') as f:
        response = requests.post(f'{base_url}/api/predict/cnn', files={'image': f})

    print(f"Status : {response.status_code}")
    print(response.json())
