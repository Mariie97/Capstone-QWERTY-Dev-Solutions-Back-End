pipeline {
	agent { docker { image 'python:3.8' } }
	stages {
		stage('BUILD') {
			steps{
				sh 'source /home/cory/Desktop/py-envs/parapido-venv/bin/activate'
				sh 'pip install -r requirements.txt'
			}
		}
		stage('TEST') {
			steps{
				sh 'python test.py'
			}
		}
	}
}
