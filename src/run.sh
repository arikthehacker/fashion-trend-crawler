#!/bin/bash
#############################################################
# run.sh
# last edited: 07/06/2026
# runs the full pipeline in order so you dont have to
# remember all the commands
#
# ways to use:###############################################
#    bash run.sh
#############################################################
set -e

echo "---------------------------------------------------"
echo "  fashion-trend-crawler −∘♥∘− full pipeline"
echo "---------------------------------------------------"

echo ""
echo "step 1: crawling fashion sources..."
python crawler.py

echo ""
echo "step 2: classifying + summarizing + saving dated report..."
python summarize.py

echo ""
echo "pipeline complete."
