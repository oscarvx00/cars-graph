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
                }
            }
            post {
                success {
                    archiveArtifacts 'ia-classifier-train/model.zip'
                }
            }
        } 
    }
}