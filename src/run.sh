#!/bin/bash
#############################################################
# run.sh
# last edited: 05/04/2026
# runs the full pipeline in order so you dont have to
# remember all the commands
#
# ways to use:###############################################
#    bash run.sh
#############################################################

echo "---------------------------------------------------"
echo "  fashion-trend-crawler −∘♥∘− full pipeline"
echo "---------------------------------------------------"

echo ""
echo "step 1: crawling fashion sources..."
python crawler.py

echo ""
echo "step 2: running tests..."
python test_tools.py

echo ""
echo "step 3: starting mcp server..."
echo "  press ctrl+c to stop when done."
echo ""
python server.py
