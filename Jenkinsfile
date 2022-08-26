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
                    stash inclides: 'model.zip', name: 'model'
                }
            }
            /*
            post {
                success {
                    archiveArtifacts 'ia-classifier-train/model.zip'
                }
            }*/
        }
        stage('Generate ia workspace'){
            agent any
            dir('ia-classifier'){
                unstash 'model'
                sh 'unzip model.zip'
                sh 'zip -r ./* ia-classifier.zip'
            }
        }
        post {
            success {
                archiveArtifacts 'ia-classifier/ia-classifier.zip'
            }
        }
    }
}