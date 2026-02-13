#!/bin/bash

echo "============================================================"
echo "🚀 STREAMLIT DASHBOARD IS STARTING..."
echo "👉 Open your browser at: http://localhost:8501"
echo "============================================================"

streamlit run dashboard.py \
  --server.port=8501 \
  --server.address=0.0.0.0
