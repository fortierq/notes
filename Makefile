run:
	poetry run streamlit run app.py

docker:
	poetry run streamlit run app.py --server.headless true --server.port 8501 --server.address 0.0.0.0
