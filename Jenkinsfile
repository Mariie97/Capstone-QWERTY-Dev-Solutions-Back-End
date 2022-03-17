pipeline {
	agent any
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
