#!/bin/bash
set -e

echo "python collect.py"
python collect.py

echo "python embedding.py --mode articles"
python embedding.py --mode articles

echo "python cluster.py"
python cluster.py

echo "python embedding.py --mode stories"
python embedding.py --mode stories

echo "python image.py"
python image.py

echo "python digest.py"
python digest.py

echo "python timelines.py"
python timelines.py