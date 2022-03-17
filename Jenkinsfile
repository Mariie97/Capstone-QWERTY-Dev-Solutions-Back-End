pipeline {
	agent { dockerfile { filename 'Dockerfile.build' } }
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
