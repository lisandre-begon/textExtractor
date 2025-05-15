#To launch before anything else, assure to be in the venv with java 11

# Activate Python venv
source ~/Projet/enviPath/textExtractor/venv10/bin/activate

# Force Java 11 for this session
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

echo "🔧 Project environment ready: Python venv10 + Java 11"
java -version
