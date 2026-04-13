setup:
	pip install -r requirements.txt

pipeline:
	python load_data.py
	python run_analysis.py

dashboard:
	streamlit run app.py