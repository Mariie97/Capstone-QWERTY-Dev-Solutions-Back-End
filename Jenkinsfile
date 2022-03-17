pipeline {
	agent { docker { image 'python:3.8' } }
	stages {
		stage('BUILD') {
			steps{
				echo 'Building...'
			}
		}
		stage('TEST') {
			steps{
				sh """ 
					python test.py
				"""
			}
		}
	}
}
