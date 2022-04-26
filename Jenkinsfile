pipeline {
	agent { dockerfile true }
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
                stage('ENVIRONMENT DISPLAY') {
                        steps{
                            echo "The env var: ${env.TEST_VAR}"
                        }
                }   
	}
}
