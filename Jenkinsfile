pipeline {
	agent { docker { image 'python:3.8' } }
	stages {
		stage('BUILD') {
			steps{
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
