pipeline {
	agent { docker { image 'python:3.8' } }
	stages {
		stage('BUILD') {
			steps{
				echo 'Building'
			}
		}
		stage('TEST') {
			steps{
				sh """ 
					source /home/cory/Desktop/py-envs/parapido-venv/bin/activate
					pip install -r requirements.txt
					python test.py
				"""
			}
		}
	}
}
