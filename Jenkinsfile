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
	}
        post {
              always {junit 'test-reports/*.xml'}
  	}
}
