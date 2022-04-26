pipeline {
	agent { dockerfile true }
	stages {
		stage('BUILD') {
			steps{
				echo 'Building...'
			}
		}
		stage('TESTS') {
			parallel{
				stage('TEST 1') {
					steps{
						sh """ 
							python test.py
						"""
					}
				}
				stage('TEST 2') {
					steps{
						sh """ 
							python test.py
						"""
					}
				}
			}
		}
		stage('ENVIRONMENT DISPLAY') {
			steps{
				echo "The env var: ${env.TEST_VAR}"
				}
		}
	}

	post {
		always {junit 'test-reports/*.xml'}
	}
}
