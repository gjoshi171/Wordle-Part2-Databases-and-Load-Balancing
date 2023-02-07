wordvalidation: uvicorn --port ${PORT:-5000} wordvalidation:app --reload
answerchecking: uvicorn --port ${PORT:-5001} answerchecking:app --reload
statistics: uvicorn --port ${PORT:-5002} statistics:app --reload
traefik: ./traefik --configFile=traefik.toml