pipeline  {
    stages {
        stage('Train ia'){
            agent {
                docker { image 'oscarvicente/cars-graph-train'}
            }
            steps {
                dir('ia-classifier'){
                    sh 'python3 data-classifier.py'
                }
            }
        }
    }
}