#!/bin/bash
python simulatioData.py &  # Script de adquisición en segundo plano
streamlit run dashboard.py --server.port $PORT --server.address 0.0.0.0
