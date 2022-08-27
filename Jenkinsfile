pipeline  {
    agent none
    stages {
        stage('Train ia'){
            agent {
                docker { image 'oscarvicente/cars-graph-train'}
            }
            steps {
                dir('ia-classifier-train'){
                    sh 'python3 data-classifier.py'
                    sh "zip -r model.zip model/*"
                    stash includes: 'model.zip', name: 'model'
                }
            }
        }
        stage('Generate product'){
            agent any
            steps {
                dir('ia-classifier'){
                    unstash 'model'
                    sh 'unzip -o model.zip'
                    sh 'rm model.zip'
                }
                sh 'zip -r cars-graph.zip ia-classifier data-getters run.sh'
            }
            post {
                success {
                    archiveArtifacts 'cars-graph.zip'
                }
            }
        }
    }     
}